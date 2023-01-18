import sys
import wave
import numpy as np
import itertools
from textblob import TextBlob, Word
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QFileDialog, QTextEdit, QLineEdit, QCheckBox, QDialog, QDial
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtCore import QSize, Qt
from sklearn.preprocessing import minmax_scale
import openai
import random
import os
import re
import ast
import requests
from PIL import Image
from PIL import PngImagePlugin
from io import BytesIO




class WavToPromptGUI(QWidget):
    maximum_tokens = None
    
    class API_VERIFICATION(QDialog):
        def  __init__(self,parent=None):
            super().__init__(parent)
                
            # Api input and label
            self.apikey_input = QLineEdit()
            self.apikey_input.setEchoMode(QLineEdit.Password)
            self.api_label = QLabel("Enter API KEY: ")
        
        
            #API KEY BUTTON
                
            self.api_button = QPushButton("USE API KEY")
            self.api_button.move(75,10)
            self.api_button.clicked.connect(self.submit_key)

            #API Layout
            api_layout = QVBoxLayout()
            api_layout.addWidget(self.api_label)
            api_layout.addWidget(self.apikey_input)
            api_layout.addWidget(self.api_button)

                
            self.setLayout(api_layout)
            self.setWindowTitle("API KEY VERIFICATION")
            self.setFixedSize(300,100)
        
        def submit_key(self):
            ai_key = self.apikey_input.text()
            try:        
            # Initialize AI model
                openai.api_key = str(ai_key)
                print("Api-Key set: " + str(ai_key))
                
            except Exception as e:
                print(e)
            else:
                self.accept()
                
    def __init__(self):
        super().__init__()
        
        #self.images_layout = QHBoxLayout()
        self.image_labels = []
        self.img_prompt = ""
        self.initUI()

    def initUI(self):
        self.api_verification = WavToPromptGUI.API_VERIFICATION()
        self.api_verification.exec_()

        # Window 1
        self.setGeometry(550, 400, 400, 350)
        self.setWindowTitle("Turn your music into an image!")

        self.label = QLabel("Select a WAV file:", self)
        self.label.move(20, 20)
            #Seed 
        self.seed = " ."

        # AI Thought Bubble window
        self.w = QWidget()
        self.b = QLabel(self.w)
        self.b.setFixedSize(400,20)
        self.b.setText(" ")
        self.w.setGeometry(650,575,300,95)
        self.b.move(75,10)
        self.w.setWindowTitle("Ai_Thought_Bubble")
        
        # Button 1 Def
        self.button1 = QPushButton("Browse", self)
        self.button1.move(20, 45)
        self.button1.clicked.connect(self.button1clicked)
        
        # Button 2 Def
        self.button2 = QPushButton("Convert File to Raw Data", self.w)
        self.button2.move(50, 30)
        self.button2.clicked.connect(self.button2clicked)
        self.button2.setVisible(False)

        # Button 3 Def
        self.button3 = QPushButton("Consult Digital Wizards", self.w)
        self.button3.move(55, 10)
        self.button3.clicked.connect(self.button3clicked)
        self.button3.setVisible(False)

        # Button 4 Def
        self.button4 = QPushButton("Generate Images", self.w)
        self.button4.move(80,25)
        self.button4.clicked.connect(self.button4clicked)
        self.button4.setVisible(False)


        # Include Lyrics checkbox
        self.include_lyrics_checkbox = QCheckBox("Include lyrics in algorithm?", self)
        self.include_lyrics_checkbox.move(20,80)
        self.include_lyrics_checkbox.stateChanged.connect(self.toggleLyricsInput)
        lyrics_box_size = QSize(300, 200)

        # Include Lyrics textbox
        self.lyrics_input = QTextEdit(self)
        self.lyrics_input.move(20,110)
        self.lyrics_input.setFixedSize(lyrics_box_size)
        self.lyrics_input.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.lyrics_input.setVisible(False)
        
        # Dial
        self.tempdial = QDial(self.w)
        self.tempdial.setRange(10,99)
        self.tempdial.setValue(70)
        self.tempdial.setWrapping(False)
        self.tempdial.setNotchesVisible(True)
        self.tempdial.setTracking(True)
        self.tempdial.setSingleStep(1)
        self.tempdial.valueChanged.connect(self.tempchanged)
        self.tempdial.setGeometry(45,45,35,35)
        self.tempdial.setVisible(False)
        
        # Complexity Label
        self.temp_dial_label = QLabel(self.w)
        self.temp_dial_label.setText("AI Model Temperature: .")
        self.temp_dial_label.move(85,55)
        self.temp_dial_label.setVisible(False)
        
        # Dial Value LineEdit
        self.temp_value = QLineEdit(self.w)
        self.temp_value.move(225,50)
        self.temp_value.setText(str(self.tempdial.value()))
        self.temp_value.setFixedSize(20,30)
        self.temp_value.setVisible(False)

        # Dial Value Validator
        self.temp_valid = QIntValidator(1, 99, self.w)
        self.temp_value.setValidator(self.temp_valid)

        


    def show_api_event(self,api_event):
            self.api_dialog = API_VERIFICATION(self)
            api_dialog.show()
            self.api_dialog.exec_()
        

    
    def toggleLyricsInput(self, state):
        if state == Qt.Checked:
            self.lyrics_input.setVisible(True)
            
        else:
            self.lyrics_input.setVisible(False)
            
        
    def tempchanged(self,value):
        self.temp_value.setText(str(value))
        self.__class__.temperature = self.temp_value.text()
        self.__class__.temperature = int(self.__class__.temperature) / 100
            

    def button1clicked(self):
        lyr_prompt = self.lyrics_input.isVisible()
        lyrics = self.lyrics_input.toPlainText()
        try:
            if lyr_prompt:
                print("Lyrics Set: \n" + lyrics)
            else:
                pass
        except Exception as e:
            print(e)
        self.wav_file, _ = QFileDialog.getOpenFileName(self, "Open WAV file", "", "WAV files (*.wav)")
        self.w.show()
        self.button2.setVisible(True)
        self.setVisible(False)

    def button2clicked(self):
        self.button2.setVisible(False)
        self.b.setText("Opening WAV file..")
        
        
        # Open the WAV file and read the audio data
        try:
            wav = wave.open(self.wav_file, "r")
            audio_data = wav.readframes(-1)
            wav.close()
        except Exception as e:
            print("Trouble with wav file.", e)

        
        # Convert the audio data from bytes to a NumPy array
        audio_data = list(np.frombuffer(audio_data, dtype=np.int16))
                    
        # Create audio_data_array for later use
        audio_data_array = np.array ([audio_data])
        array_size = audio_data_array.size
    
        
        print("Array Size: [" + str(array_size) + "] integers")
                
        # Reverse the order of the elements in the data array (For a more unique output)
        audio_data = np.flip(audio_data)
                
        # Define sample_size
        sample_size = 10

        # Group audio_data_array into as many groups as sample_size
        if array_size % 10 == 0:
            groups = np.reshape(audio_data_array, (-1,sample_size))
        else:
            remainder = array_size % 10
            audio_data_array = np.delete(audio_data_array, range(remainder))
            groups = np.reshape(audio_data_array, (-1,sample_size))

        #print(groups)
                
        # Use groups array to create 10 unique numbers as pre_letters
        mean_array =  np.mean(groups, axis=0)
        try:
            self.pre_letters = mean_array.tolist()
            #print(pre_letters)
        except Exception as e:
            print("Error: ",e)
            
                        
                
        # Create seed value based on audio_data
        audio_data_sum = audio_data.sum()
        audio_data_sum = audio_data_sum*audio_data_sum
        seed_val = int(audio_data_sum)
        seed_val = seed_val // 1000000000
        
       
        self.b.move(77,10)
        # Set seed
        try:
            np.random.seed(seed_val)
        except Exception as e:
            print("Seed Failed: ",e)
        # Update seed
        self.seed = seed_val
        print("Seed found: [" + str(self.seed) + "]")

        # Create seeds for Prompt
        # Pre-Prompt seed

        pre_lib_seed = []
        pre_lib_indices = [0,4,9]
        for index in pre_lib_indices:
            num = self.pre_letters[index]
            num = str(num)[-6:]
            pre_lib_seed.append(int(num))
        print(str(pre_lib_seed))
        
        # Iterate to create new seed for pre
        try:
            counter = 0
            for value in pre_lib_seed:
                if counter == 0:
                    pre_seed = seed_val % value
                elif counter == 1:
                    pre_seed = pre_seed * value
                elif counter == 2:
                    self.pre_seed = int(pre_seed / value)
                else:
                    counter = 0
                    continue
                counter += 1
            print("Pre Seed: " + str(self.pre_seed))
        except Exception as e:
            print("Problem with Pre Seed: " , e)
        

        # Sentence Seed
        sent_lib_seed = []
        sent_lib_indices = [3,5]
        for index in sent_lib_indices:
            num = self.pre_letters[index]
            num = str(num)[-6:]
            sent_lib_seed.append(int(num))
        print(str(sent_lib_seed))

        # Iterate to create new seed for sentence
        try:
            counter = 0
            for value in sent_lib_seed:
                if counter == 0:
                    sent_seed = seed_val + value
                elif counter == 1:
                    self.sent_seed = int(sent_seed / value)
                else:
                    counter = 0
                    continue
                counter += 1
            
            print("Sentence Seed: " + str(self.sent_seed))
        except Exception as e:
            print("Problem with Sentence Seed: " , e)
    
        

        
            
            
        self.b.setText("")
        self.button3.setVisible(True)
        self.temp_value.setVisible(True)
        self.temp_dial_label.setVisible(True)
        self.tempdial.setVisible(True)
        
        

    def button3clicked(self):
                    self.__class__.temperature = self.temp_value.text()
                    self.__class__.temperature = int(self.__class__.temperature) / 100
                    try:
                        print("Temperature Set: " + str(self.__class__.temperature))
                    except Exception as e:
                        print(e)

                    self.button3.setVisible(False)
                    self.temp_value.setVisible(False)
                    self.temp_dial_label.setVisible(False)
                    self.tempdial.setVisible(False)
                    lyrics = self.lyrics_input.toPlainText()
                    
                    # Define empty list
                    numlist = []

                    # Iterate pre_letters to calculate numbers between 1 and 26
                    try:
                        for item in self.pre_letters:
                            item = str(item)
                            item  = item[-6:]
                            item = int(item)
                            num = item % 26
                            numlist.append(num)
                    except Exception as e:
                        print("Error iterating over pre_letters: ", e)
                    #print(numlist)
                    

                    # Map numbers to letters
                    number_dict = { 
                          1: "A",
                          2: "B",
                          3: "C",
                          4: "D",
                          5: "E",
                          6: "F",
                          7: "G",
                          8: "H",
                          9: "I",
                          10: "J",
                          11: "K",
                          12: "L",
                          13: "M",
                          14: "N",
                          15: "O",
                          16: "P",
                          17: "Q",
                          18: "R",
                          19: "S",
                          20: "T",
                          21: "U",
                          22: "V",
                          23: "W",
                          24: "X",
                          25: "Y",
                          26: "Z"
                        }

                        
                    # Create string to hold letters
                    letters = ""

                    # Iterate over the numbers in the string
                    try:
                        for x in numlist:
                            if x == 0:
                                letter = random.choice(list(number_dict.values()))
                                letters += letter
                            else:
                                letters += number_dict.get(x)
                    except Exception as e:
                        print("Error iterating over numlist: ", e )
            
                    print(letters)

                
                    # Create empty string for words
                    word_str = " "
                
                    # Create a list from the 1st, 5th and 10th letters
                    try:
                        letters = letters.lower()
                        letters = list(letters)
                        # .pop removes the letter from the list, so the indices must be -1 for each iteration
                        
                        indicesfft = [0,3,7] # 1st, 5th, 10th ADJ
                        fft_letters = []
                        for index in indicesfft:
                            if 0 <= index < len(letters):
                                let = letters.pop(index)
                                fft_letters.append(let)
                        print("FFT: ",fft_letters)
                                
                        indicesst = [0,0] # 2nd, 3rd NOUN
                        st_letters = []
                        for index in indicesst:
                            if 0 <= index < len(letters):
                                let = letters.pop(index)
                                st_letters.append(let)
                        print("ST: ",st_letters)

                        indicesfe = [0,2] # 4th, 8th VERB
                        fe_letters = []
                        for index in indicesfe:
                            if 0 <= index < len(letters):
                                let = letters.pop(index)
                                fe_letters.append(let)
                        print("FE: ",fe_letters)
                        
                        indicesss = [0,0] # 6th, 7th NOUN
                        ss_letters = []
                        for index in indicesss:
                            if 0 <= index < len(letters):
                                let = letters.pop(index)
                                ss_letters.append(let)
                        print("SS: ", ss_letters)     

                        ninth_letter = letters # 9th VERB
                        print("N: ",ninth_letter)
                    except Exception as e:
                        print("Problem creating letter lists: ", e)
                
                    # Define POS
                    # ADJ
                    adjectives = []
                    with open("DICTIONARY/adjectives_list.txt", "r") as adj_file:
                        adjectives = adj_file.readlines()
                    print("Adjectives Loaded")
                    #adjectives = adjectives.split('\n')
                    adjectives = [line.strip() for line in adjectives]
                    #print(adjectives)

                    # NOUNS
                    nouns = []
                    with open("DICTIONARY/noun_list.txt", "r") as noun_file:
                        nouns = noun_file.readlines()
                    print("Nouns Loaded")
                    nouns = [line.strip() for line in nouns]
                    #print(nouns)

                    #VERBS
                    verbs = []
                    with open("DICTIONARY/verb_list.txt", "r") as verb_file:
                            verbs = verb_file.readlines()
                    print("Verbs Loaded")
                    verbs = [line.strip() for line in verbs]
                    #print(verbs)
                    

                    
                    # 1,5,10 Adj
                    # First filter adjectives by 1st letter of fft_letters
                    
                    fft_adjs = []
                    try:
                        for word in adjectives:
                            if word[0] == fft_letters[0]:
                                fft_adjs.append(word)
                            elif word[0] == fft_letters[1]:
                                fft_adjs.append(word)
                        #print(fft_adjs)
                    except Exception as e:
                        print(e)
                        
                    fft_found = False
                    filtered_adj = []
                    # Filter the rest of the letters
                    while not fft_found:
                        try:
                            for adj in fft_adjs:
                                if all(letter in adj for letter in fft_letters):
                                    filtered_adj.append(adj)
                                else:
                                    del fft_letters[0]
                                    continue
                            #print(filtered_adj)
                            chosen_fft = np.random.choice(filtered_adj)
                            print(chosen_fft)
                            ADJ = chosen_fft
                            fft_found = True
                        except Exception as e:
                            print("ADJ FILTER ERROR: ",e)
                            

                    # 2,3 + 6,7 Noun
                    
                    # First letter of 2,3
                    st_nouns = []
                    try:
                        for word in nouns:
                            if word[0] == st_letters[0]:
                                st_nouns.append(word)
                        #print(st_nouns)
                    except Exception as e:
                        print("ST NOUN FIRST LETTER ERROR: ",e)

                    st_found = False
                    filtered_st_nouns = []
                    # Filter to include 3
                    while not st_found:
                        try:
                            for noun in st_nouns:
                                if all(letter in noun for letter in st_letters):
                                    filtered_st_nouns.append(noun)
                            #print(filtered_st_nouns)
                            chosen_st = np.random.choice(filtered_st_nouns)
                            print(chosen_st)
                            NOUN = chosen_st
                            st_found = True
                        except Exception as e:
                            print("ST FIND ERROR: ",e)

                    # First letter of 6,7
                    ss_nouns = []
                    try:
                        for word in nouns:
                            if word[0] == ss_letters[0]:
                                ss_nouns.append(word)
                        #print(ss_nouns)
                    except Exception as e:
                        print("SS NOUNS FIRST LETTER ERROR: ",e)

                    ss_found = False
                    filtered_ss_nouns = []
                    # Filter to include 7
                    while not ss_found:
                        try:
                            for noun in ss_nouns:
                                if all(letter in noun for letter in ss_letters):
                                    filtered_ss_nouns.append(noun)
                                else:
                                    del ss_letters[0]
                                    continue
                            #print(filtered_ss_nouns)
                            chosen_ss = np.random.choice(filtered_ss_nouns)
                            print(chosen_ss)
                            NOUN2 = chosen_ss
                            ss_found = True
                        except Exception as e:
                            print("SS FIND ERROR:",e)
                    

                    # 4,8 + 9 Verb

                    # First letter of 4,8
                    fe_verbs =[]
                    try:
                        for word in verbs:
                             if word[0] == fe_letters[0]:
                                fe_verbs.append(word)
                        #print(fe_verbs)
                    except Exception as e:
                        print("FE VERBS FIRST LETTER ERROR: ",e)

                    fe_found = False
                    filtered_fe_verbs = []
                    # Filter to include 8
                    while not fe_found:
                        try:
                            for verb in fe_verbs:
                                if all(letter in verb for letter in fe_letters):
                                    filtered_fe_verbs.append(verb)
                           # print(filtered_fe_verbs)
                            chosen_fe = np.random.choice(filtered_fe_verbs)
                            print(chosen_fe)
                            VERB = chosen_fe 
                            fe_found = True
                        except Exception as e:
                            print("FE FIND ERROR:",e)


                    # Find 9
                    ninth_verbs =[]
                    try:
                        for word in verbs:
                            if word[0] == ninth_letter[0]:
                                ninth_verbs.append(word)
                        #print(ninth_verbs)
                        chosen_ninth = np.random.choice(ninth_verbs)
                        print(chosen_ninth)
                        VERB2 = chosen_ninth
                    except Exception as e:
                        print("NINTH VERB ERROR: ",e)
        

                    
                    # Assemble MadLibs Puzzle
                    PLURAL_NOUN = ''
                    PAST_TENSE_VERB = ''
                    ASSIGNED_WORDS = [ADJ, NOUN, NOUN2, VERB, VERB2,PLURAL_NOUN,PAST_TENSE_VERB]
                    # Open Prefixes
                    try:
                        with open('PROMPT_FILES/MadLib_pre.txt', 'r') as file:
                            pre_lib = file.read()
                        pre_lib = ast.literal_eval(pre_lib)
                        #print("Prelibs Loaded: " + str(pre_lib))

                        # CHOOSE PREFIX
                        prelib_index = self.pre_seed % len(pre_lib)
                        chosen_prelib = str(pre_lib[prelib_index])
                        #print("Prelib chosen: " + str(chosen_prelib))

                        # Open Sentences
                        with open('PROMPT_FILES/MadLib_sent.txt', 'r') as file:
                            sent_lib = file.read()
                        sent_lib = ast.literal_eval(sent_lib)
                        print("Sentences Loaded: " + str(sent_lib))

                        # CHOOSE SENTENCE
                        sent_index = self.sent_seed % len(sent_lib)
                        chosen_sent = str(sent_lib[sent_index])
                        #print("Sentence chosen: "+ str(chosen_sent))
                    except Exception as e:
                       print("MADLIBS PUZZLE ERROR: ",e)

                    
                    # CHECK FOR NON STANDARD POS
                    try:
                        if chosen_sent.count("{PLURAL_NOUN}") == 0:
                            ASSIGNED_WORDS[5]=""
                            pass
                        if chosen_sent.count("{PLURAL_NOUN}") ==1:
                            PLURAL_NOUN = Word(NOUN2).pluralize()
                            ASSIGNED_WORDS[5]=PLURAL_NOUN
                            # REFORMAT
                            #formatted_sent = formatted_sent.format(PLURAL_NOUN=PLURAL_NOUN)

                        if chosen_sent.count("{PAST_TENSE_VERB}") == 0:
                            ASSIGNED_WORDS[6] = ""
                            pass
                        if chosen_sent.count("{PAST_TENSE_VERB}") == 1:
                            try:
                                pl_verbs = []
                                if TextBlob("VERB2").pos_tags[0][1] == 'VBD':
                                        pass
                                else:
                                        for words in ninth_verbs:
                                            text_blob = TextBlob(words)
                                            if any(tag[1] in ['VBD'] for tag in text_blob.pos_tags):
                                                pl_verbs.append(words)
                                        PAST_TENSE_VERB = np.random.choice(pl_verbs)
                                        ASSIGNED_WORDS[6]=PAST_TENSE_VERB
                                print(PAST_TENSE_VERB)
                                # REFORMAT
                                #formatted_sent = formatted_sent.format(PAST_TENSE_VERB=PAST_TENSE_VERB)
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        print("NON STANDARD POS ERROR: ",e)
                        

                    try:

                        formatted_prelib = chosen_prelib.format(ADJ=ASSIGNED_WORDS[0])
                        formatted_sent = chosen_sent.format(NOUN=ASSIGNED_WORDS[1],NOUN2=ASSIGNED_WORDS[2],
                                                            VERB=ASSIGNED_WORDS[3],VERB2=ASSIGNED_WORDS[4],
                                                            PLURAL_NOUN=ASSIGNED_WORDS[5],PAST_TENSE_VERB=ASSIGNED_WORDS[6])
                    except Exception as e:
                        print("FORMATTING ERROR: ",e)


                    print(ASSIGNED_WORDS)
                    davinci_prompt = formatted_prelib + " " + formatted_sent
                    
                    print(davinci_prompt)

                        

                    # Davinci 003
                    if len(lyrics) > 1:
                        lyr_prompt = True
                    else:
                        lyr_prompt = False
                    print(lyr_prompt)
                    
                    if lyr_prompt:
                        lyrics_pre =  lyrics + "'\n Are lyrics to the song that inspired the image that this prompt is describing: "
                        lyrics_post = " Generate a very similar new prompt, with around the same number of tokens.  Pull any possible imagery from the lyrics."
                    else:
                        lyrics_pre = "Here is a description of an image inspired by a piece of music: "
                        lyrics_post = "Generate a very similar new prompt, with around the same number of tokens. "

                    try:
                        madlib_completion = openai.Completion.create(
                                    engine = "text-davinci-003",
                                    prompt = lyrics_pre + davinci_prompt + lyrics_post,
                                    temperature = self.__class__.temperature ,
                                    max_tokens = 70,
                        )
                    except Exception as e:
                        print("Problem with DaVinci: ", e)
                    for choice in madlib_completion.choices:
                        self.madlib_output = choice.text.split()
                        self.img_prompt = ' '.join(self.madlib_output)
                    print(self.img_prompt)
                    

                    self.button4.setVisible(True)
        
                    print("[DONE]")

                               
    def button4clicked(self):
        self.button4.setVisible(False)

        # Open Dalle prefixes
        with open("PROMPT_FILES/pre_dalle.txt", "r") as file:
            pre_dalle = file.read()
            
        dalle_prefixes = ast.literal_eval(pre_dalle)

        print("Prefixes loaded")

        # Get the sum of seed_val
        try:
            self.seed = str(self.seed)
            seed_sum = 0
            for dig in self.seed:
                seed_sum += int(dig)
            print(seed_sum)
        except Exception as e:
            print(e)

        # Use sum to choose prefix
        prefix_index = seed_sum % len(dalle_prefixes)
        selected_prefix = dalle_prefixes[prefix_index]

        print("Prefix selected: " + selected_prefix)
                
                

        try:
            #Convert img_prompt into image
            self.new_prompt = (selected_prefix + self.img_prompt)
            print(self.new_prompt)
        except Exception as e:
            print(e)
        try:
            gen_image = openai.Image.create(
                   prompt=self.new_prompt,
                   n=3,
                   size="1024x1024"
               )
        except Exception as e:
            print("Error generating image: ", e)
                        
        img_found = True
        print("Images Generated")

                    
        if img_found:
            images = []
            try:
                data = gen_image['data']
                for item in data:
                    #print("iterating over items")
                    image_url = item['url']
                    images.append(image_url)
            except Exception as e:
                print(e)
                
            counter = 1
            for img_ in images:
                # Define image directory
                img_dir = "./Generated Images"
                # Set base file name for image file
                image_name = "gen_img_" + str(counter)
                # Add prompt as description to file name
                img_desc = "'" + self.img_prompt + "'"
                image_path = os.path.join(img_dir, image_name + ".png")
                # Check if file by same name exists, add suffix if true
                try:
                    if os.path.exists(image_path):
                        image_name = image_name +  "_1"
                        image_path = os.path.join(img_dir, image_name + ".png")
                except Exception as e:
                    print("Pathing error: ",e)
                # Save image_url   
                try:
                    saved_img = requests.get(img_) 
                    # Open Image
                    img = Image.open(BytesIO(saved_img.content))
                    # Save description
                    img.info["Description"] = img_desc
                    #Save image
                    img.save(image_path, "PNG")
                    print("image saved as: " + image_name)
                    img.show()
                    counter += 1
                except Exception as e:
                        print("Error saving image: ", e)
                #print(img_desc)
              

               
                    

                
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WavToPromptGUI()
    window.show()
    sys.exit(app.exec_())
