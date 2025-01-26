from src.data.parse_movie_script import MovieScriptParser
from io import StringIO

def test_get_scene_name():
	assert (MovieScriptParser._get_scene_name("1\tscene") == "scene")
	assert (MovieScriptParser._get_scene_name("x\tscene") is None)
	assert (MovieScriptParser._get_scene_name("xscene") is None)

def test_parse_text_script_empty_scenes():
	text = """
	Title
1\tSCENE NAME 1

2\tSCENE NAME 2

2\tSCENE NAME 3
THE END
"""
	parsed_object = MovieScriptParser._parse_text_script(StringIO(text))
	structured_script = parsed_object.scenes

	assert (len(structured_script) == 4)
	assert (len(structured_script[0].entries) == 1)
	assert (len(structured_script[1].entries) == 0)
	assert (len(structured_script[2].entries) == 0)
	assert parsed_object.stats["total_characters"] == 0
	assert parsed_object.stats["total_dialogues"] == 0
	assert parsed_object.stats["total_scenes"] == 4

def test_parse_text_script_only_character_no_description():
	text = """
	Title
1\tSCENE NAME 1
	Some scene description	
2\tSCENE NAME 2
\t\t\t\t\t\tCHARACTER X
\t\t\t\tSome dialogue.	
THE END
	"""
	parsed_object = MovieScriptParser._parse_text_script(StringIO(text))
	structured_script = parsed_object.scenes

	assert (len(structured_script) == 3)
	assert (len(structured_script[0].entries) == 1)
	assert (len(structured_script[1].entries) == 1)
	assert (structured_script[2].entries[0].dialogue.character == "CHARACTER X")
	assert parsed_object.stats["total_characters"] == 1
	assert parsed_object.stats["total_dialogues"] == 1
	assert parsed_object.stats["total_scenes"] == 3

def test_parse_text_script_only_description():
	text = """
	Title
1\tSCENE NAME 1
	Some scene description	
2\tSCENE NAME 2
	More scene description	
THE END
	"""
	parsed_object = MovieScriptParser._parse_text_script(StringIO(text))
	structured_script = parsed_object.scenes

	assert (len(structured_script) == 3)
	assert (len(structured_script[0].entries) == 1)
	assert (len(structured_script[1].entries) == 1)
	assert (len(structured_script[2].entries) == 1)
	assert structured_script[0].entries[0].dialogue is None
	assert structured_script[1].entries[0].dialogue is None
	assert structured_script[2].entries[0].dialogue is None
	assert parsed_object.stats["total_characters"] == 0
	assert parsed_object.stats["total_dialogues"] == 0
	assert parsed_object.stats["total_scenes"] == 3

def test_parse_text_script_mixed_text():
	text = """				The Fifth Element

				An original script
				by
				Luc Besson

				Revisions by
				Luc Besson
				and
				Robert Mark Kamen

				August 1995 Draft

				Gaumont and Les Films du Dauphin

FADE IN:

1	EXT.  DESERT  NILE RIVER  VALLEY - DAY

	Somewhere in the Nile at the edge of the desert.

	CREDITS  ROLL

	WRITTEN:	EGYPT 1913

	OMAR and his mule zigzag along the bottom of sun scorched dunes.

2	EXT.  TEMPLE  EXCAVATION - DAY

	The mule and the boy finally reach a camp.  A few tents dwarfed by a huge
temple door jutting out of the sand.  The camp is deserted except for
some kids by the temple entrance holding large mirrors, reflecting light
into the temple.
	Omar leaves his mule in the shade, seizes two goatskins and slips inside
the temple.

3	INT.  TEMPLE - DAY

	Omar makes his way uneasily down a pillared corridor that opens into a
vast room where an old scientist stands on a small wooden ladder in front of
the wall across the room.  PROFESSOR MASSIMO PACOLI. A young man is beside
him, BILLY MASTERSON, age 25, an American student. He has a large sketchpad in
his hands.  Behind them AZIZ, age 10, whose job is to hold the last
mirror which shines light into the expansive room.

						PROFESSOR
					(deciphering)
				"..when the three planets are in eclipse.."

	His fingers trace across the wall which is covered with symbols and
strange hieroglyphs as he deciphers.

						PROFESSOR
				"..the black hole like a door is open...
				Evil comes ... sowing terror and chaos..."
				See?  The snake, Billy.  The Ultimate Evil
				... make sure you get the snake!

	The Professor points emphatically to the snake, the symbol of Evil,
coming through the door between the three planets in eclipse.  C.U.
Billy's hand sketches the snake quickly.  He is a natural artist.

						BILLY
				And when is this door opening snake act
				supposed to occur?

	The Professor's fingers touch the signs.

THE END
"""
	parsed_object = MovieScriptParser._parse_text_script(StringIO(text))
	structured_script = parsed_object.scenes

	assert (len(structured_script) == 4)
	assert (len(structured_script[0].entries) == 1)
	assert (len(structured_script[1].entries) == 1)
	assert (len(structured_script[2].entries) == 1)
	assert (len(structured_script[3].entries) == 4)
	assert (structured_script[3].entries[0].dialogue.character == "PROFESSOR")
	assert (structured_script[3].entries[1].dialogue.character == "PROFESSOR")
	assert (structured_script[3].entries[2].dialogue.character == "BILLY")
	assert (structured_script[3].name == "INT.  TEMPLE - DAY")
	assert parsed_object.stats["total_characters"] == 2
	assert parsed_object.stats["total_dialogues"] == 3
	assert parsed_object.stats["total_scenes"] == 4

def test_parse_text_script_mixed_text_2():
	text = """
	Some title
283	INT.  LABORATORY

	We are in the Nucleological Laboratory that gave birth to Leeloo in the
beginning of our story.  The President enters the lab followed by a group
of officials in ceremonial dress.

						MUNRO
				Mr. President, let me introduce you to
				Professor Mactilburgh, who runs the center.

						MACTILBURGH
				It's an honor to receive you. Mr. President.

						PRESIDENT
					(beaming)
				Yes.. Well? Where are our two heroes?

						MACTILBURGH
				They were so tired from their ordeal that
				we put them in the reactor this morning..

						PRESIDENT
				I have 19 more meetings after this one
				Professor..

						PROFESSOR
				Of course.. Let me see if they're revived.

						AIDE
				We go live in one minute, Mr. President.

	Mactilburgh goes to the reactor and opens a small slot which allows him
to see what is going on under the blue shield.

	Leeloo and Korben are naked, arms wrapped around each other, kissing and
probably engaged in hoppi hoppa.
	Mactilburgh looks troubled.

						MACTILBURGH
				I.. uh.. they need five more minutes,
				Mr. President.

	The President, pressed for time, looks over to his aide who in struggling
with a phone call.

						AIDE
				No ma'am... I tried... No ma'am...

						PRESIDENT
				Who is it?

						AIDE
				Some woman... claims she's Korben's
				mother...

						PRESIDENT
				Give it here...

	The President takes the phone and goes to the window.

						PRESIDENT
				Mrs. Dallas, this in the President.
				On behalf of the entire Federation,
				I would like to thank...

						MOTHER (V.O.)
				Don't pull that crap with me, Finger...
				I'd recognize that trash can voice of
				yours in a dark alley during a rain storm.
				You tell that worthless no account son
				of mine he should plotz for the way he's
				ignored his mother... when I think of all I
				sacrificed for him...

284	EXT.  NEW YORK

THE END
"""
	parsed_object = MovieScriptParser._parse_text_script(StringIO(text))
	structured_script = parsed_object.scenes

	assert (structured_script[1].entries[0].dialogue.character == "MUNRO")
	assert (structured_script[1].entries[1].dialogue.character == "MACTILBURGH")
	assert (structured_script[1].entries[-1].dialogue.character == "MOTHER (V.O.)")
