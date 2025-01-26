from pydantic import BaseModel
from typing import Optional
import re
from io import StringIO
from dataclasses import dataclass
from collections import Counter

@dataclass
class Dialogue:
    character: str
    text: str

@dataclass
class Entry:
    description: str
    dialogue: Optional[Dialogue]

@dataclass
class Scene:
    name: str
    entries: list[Entry]

class MovieScriptParser:

    @dataclass
    class ParsedObject:
        scenes: list[Scene]
        stats: dict
        character_vocabulary: list[str]

        def get_vocabulary_to_label_mapping(self):
            return {v: i for i, v in enumerate(self.character_vocabulary)}

        def get_label_to_vocabulary_mapping(self):
            return {i: v for i, v in enumerate(self.character_vocabulary)}

        def save_character_dialogue_dataset_in_json_format(self, output_filename: str):
            """
            Saves a dataset of character dialogues in JSON format.
            This method iterates through the scenes and their entries, extracting dialogues
            and mapping each character to a label based on the character vocabulary. The result
            is a list of dictionaries, each containing the dialogue text and the corresponding
            character label.

            Args:
                output_filename (str): The name of the output file where the JSON data will be saved.
                None
            """
            import json

            vocabulary_to_label_mapping = self.get_vocabulary_to_label_mapping()
            
            with open(output_filename, "w") as file:
                for entry in self.scenes:
                    for e in entry.entries:
                        if e.dialogue:
                            file.write(
                                json.dumps({
                                    "text": e.dialogue.text,
                                    "label": vocabulary_to_label_mapping[
                                        e.dialogue.character
                                    ],
                                })
                            )
                            file.write("\n")

    @dataclass
    class ParserState:
        scene_text: StringIO
        dialogue_text: StringIO
        scene_name: str
        character_name: Optional[str]
        stats: Counter
        character_vocabulary: set
        scenes: list[Scene]
        entries: list[Entry]

    @staticmethod
    def from_text_file(filename: str) -> ParsedObject:
        """
        Parse file containing input script in free text format into a structured format.
        Returns a list of Scene objects parsed from the input script text.

        Args:
            filename (str): The path to the file containing the script text.
        """
        with open(filename, "r") as file:
            return MovieScriptParser._parse_text_script(file)

    @staticmethod
    def _parse_text_script(file_like) -> ParsedObject:
        """
        Parse input script in free text format into a structured format.
        Returns a list of Scene objects parsed from the input script text.
        Note: the first scene refers to the title of the script.

        Args:
            file_like (file-like object): An object with a `.read()` or `.readline()` method.
        """
        parser_state = MovieScriptParser.ParserState(
            scene_text=StringIO(),
            dialogue_text=StringIO(),
            scene_name="SCRIPT TITLE",
            character_name=None,
            stats=Counter(),
            character_vocabulary=set(),
            scenes=[],
            entries=[],
        )

        for line in file_like:
            line = line.strip("\n")

            # Skip empty lines
            if not line:
                continue

            # Is it a new scene starting ?
            new_scene_name = MovieScriptParser._get_scene_name(line)
            if new_scene_name:
                # This is a new scene
                MovieScriptParser._add_scene(parser_state)
                parser_state.scene_name = new_scene_name

                # Reset the parser state
                MovieScriptParser._reset_buffer(parser_state.scene_text)
                MovieScriptParser._reset_buffer(parser_state.dialogue_text)
                parser_state.entries = []
                parser_state.character_name = None
            else:
                # Existing scene continues
                num_tabs = MovieScriptParser._count_leading_tabs(line)

                if num_tabs == 6:

                    if parser_state.character_name:
                        # Entry ends with a movie character, add it
                        MovieScriptParser._add_entry(parser_state)

                    # This is a new character beginning to speak
                    parser_state.character_name = line.strip()

                elif num_tabs in [4, 5] and parser_state.character_name is not None:
                    # Character is still speaking, keep adding the dialogue
                    MovieScriptParser._concatenate_text(
                        parser_state.dialogue_text, line
                    )
                else:
                    if parser_state.character_name:
                        # Entry ends with a movie character, add it
                        MovieScriptParser._add_entry(parser_state)
                        parser_state.character_name = None

                    # Add the new scene description
                    MovieScriptParser._concatenate_text(parser_state.scene_text, line)

        if parser_state.scene_text.tell() > 0 or parser_state.character_name:
            # Add the last scene
            MovieScriptParser._add_scene(parser_state)

        parser_state.stats["total_characters"] = len(parser_state.character_vocabulary)
        parser_state.stats["total_scenes"] = len(parser_state.scenes)

        return MovieScriptParser.ParsedObject(
            scenes=parser_state.scenes,
            character_vocabulary=sorted(parser_state.character_vocabulary),
            stats=parser_state.stats,
        )

    @staticmethod
    def _add_entry(parser_state: ParserState):
        """
        Adds an entry to the parser state with the current scene and dialogue text.

        This method processes the current scene and dialogue text stored in the parser state,
        creates an Entry object, and appends it to the entries list in the parser state.
        It also updates various statistics related to the script parsing process.

        Args:
            parser_state (ParserState): The current state of the parser, containing buffers
                                        for scene and dialogue text, character name, and statistics.

        Updates:
            - Appends a new Entry object to parser_state.entries.
            - Updates parser_state.stats with word counts and dialogue counts.
            - Adds the character name to parser_state.character_vocabulary if it exists.
            - Resets the dialogue buffer and character name in the parser state.
        """
        scene_text_stirng = parser_state.scene_text.getvalue()
        dialogue_text_string = parser_state.dialogue_text.getvalue()

        parser_state.entries.append(
            Entry(
                description=scene_text_stirng,
                dialogue=(
                    Dialogue(
                        character=parser_state.character_name, text=dialogue_text_string
                    )
                    if parser_state.character_name
                    else None
                ),
            )
        )

        # Do some stats counting
        scene_word_count = len(scene_text_stirng.split())
        dialogue_word_count = len(dialogue_text_string.split())
        if parser_state.character_name:
            parser_state.stats["total_dialogues"] += 1
            parser_state.stats["total_words_in_dialogues"] += dialogue_word_count
            parser_state.character_vocabulary.add(parser_state.character_name)
        parser_state.stats["total_words"] += scene_word_count + dialogue_word_count

        # Reset the dialogue buffer and character name
        parser_state.character_name = None
        MovieScriptParser._reset_buffer(parser_state.dialogue_text)
        MovieScriptParser._reset_buffer(parser_state.scene_text)

    @staticmethod
    def _add_scene(parser_state: ParserState):
        """
        Adds a scene to the list of scenes.

        This function creates a new Scene object with the provided scene_name and entries,
        and appends it to the scenes list.

        Args:
            entries (list): A list of Entry objects representing the entries in the scene.
            scene_name (str): The name of the scene.
            scene_text (io.StringIO): A StringIO buffer containing the text of the scene.
            scenes (list): A list of Scene objects to which the new scene will be added.
        """
        # Check for the last description
        if parser_state.scene_text.tell() > 0 or parser_state.character_name:
            # There is another entry to add
            MovieScriptParser._add_entry(parser_state)
        parser_state.scenes.append(
            Scene(name=parser_state.scene_name, entries=parser_state.entries)
        )

    @staticmethod
    def _reset_buffer(scene_text):
        """
        Resets the buffer of the given scene_text by seeking to the beginning and truncating its content.

        Args:
            scene_text (io.StringIO): The buffer to reset.
        """
        scene_text.seek(0)
        scene_text.truncate(0)

    @staticmethod
    def _get_scene_name(line: str) -> str:
        """
        Try to match a new scene format <number><tab><scene name> and if successful, return scene name.

        Args:
            line (str): The line of text to match.
        """
        match = re.match(r"^\d+\t.+$", line)
        return line.split("\t")[1] if match else None

    @staticmethod
    def _count_leading_tabs(input_string: str) -> int:
        """
        Count the nymber of leading tabs in the input string

        Args:
            input_string (str): the input string
        """
        count = 0
        for char in input_string:
            if char == "\t":
                count += 1
            else:
                break
        return count

    @staticmethod
    def _concatenate_text(buffer: StringIO, new_line: str):
        """
        Adds a new string to an existing StringIO buffer, removing a trailing '-' if it exists.

        Args:
            buffer (StringIO): The existing StringIO buffer.
            new_line (str): The new string to append.
        """
        # Move the cursor to the end of the buffer
        buffer.seek(0, 2)

        # Check if the buffer ends with a "-"
        if buffer.tell() > 0:  # Ensure the buffer is not empty
            buffer.seek(buffer.tell() - 1)
            if buffer.read(1) == "-":
                # Remove the trailing "-" by truncating
                buffer.seek(buffer.tell() - 1)
                buffer.truncate()

        # Append the new string
        buffer.write(new_line.strip().lower() + " ")
