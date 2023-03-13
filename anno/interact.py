import asone
import cfg
import speech_recognition as sr  # python speech recognition

def select_class_by_keyboard(key):
    class_to_id = {value: key for (key, value) in cfg.id_to_class.items()}

    try:
        class_name = cfg.key_to_class[key]
        selected_class_id = class_to_id[class_name]
        return selected_class_id
    except KeyError:
        if key == asone.ESC_KEY:
            return None


# Voice Input Class
class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def get_audio(self):
        with sr.Microphone() as source:
            print("Listening....")  ##yorum
            audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=2)
            try:
                text = self.recognizer.recognize_google(audio)
                if text == "airplay" or text == "airplanes" or text == "a airplane":
                    text = "airplane"
                elif text == "ambulence":
                    text = "ambulance"
                elif text == "antenna tower" or text == "antenna Tyler" or text == "antenna towel":
                    text = "antenna_tower"
                elif text == "Apartments" or text == "apartments" or text == "apartments":
                    text = "apartment"
                elif text == "battleships":
                    text = "battleship"
                elif text == "French" or text == "batch":
                    text = "bench"
                elif text == "bicycles":
                    text = "bicycle"
                elif text == "Bird" or text == "Birds" or text == "third" or text == "dirt":
                    text = "bird"
                elif text == "boats" or text == "Bolt" or text == "both":
                    text = "boat"
                elif text == "Bridge" or text == "bridges" or text == "Bridges":
                    text = "bridge"
                elif text == "buses" or text == "boss" or text == "Buss":
                    text = "bus"
                elif text == "cannoli" or text == "Canary" or text == "kind of" or text == "canu" or text == "kanu":
                    text = "canoe"
                elif text == "cars" or text == "call" or text == "Carr":
                    text = "car"
                elif text == "cargo ship" or text == "car dealership" or text == "cargo shop" or text == "cargoership" or text == "cargoship":
                    text = "cargo_ship"
                elif text == "cats" or text == "chats" or text == "chat":
                    text = "cat"
                elif text == "civilian UAV" or text == "civilian U" or text == "civilian new" or text == "civilian Nu" or text == "civilian UAB" or text == "civilian navy" or text == "civilian new AV" or text == "civilian uavie":
                    text = "civilian_UAV"
                elif text == "clouds" or text == "Cloud" or text == "Clouds" or text == "close" or text == "clout":
                    text = "cloud"
                elif text == "cottages" or text == "courage" or text == "Carthage" or text == "Cartage" or text == "Carthage" or text == "cartridge":
                    text = "cottage"
                elif text == "cows" or text == "Cow" or text == "Chow" or text == "ciao" or text == "child":
                    text = "cow"
                elif text == "dogs" or text == "Dogg" or text == "Doug":
                    text = "dog"
                elif text == "fields" or text == "Shield" or text == "feel" or text == "fil" or text == "shield":
                    text = "field"
                elif text == "Forest" or text == "Forests" or text == "florist" or text == "forests" or text == "Forrest":
                    text = "forest"
                elif text == "goats" or text == "gold" or text == "God":
                    text = "goat"
                elif text == "handbags" or text == "hand back" or text == "hand pack" or text == "handook" or text == "handback" or text == "hand bag":
                    text = "handbag"
                elif text == "helicopters":
                    text = "helicopter"
                elif text == "Highway":
                    text = "highway"
                elif text == "horses" or text == "course" or text == "of course" or text == "coarse":
                    text = "horse"
                elif text == "houses" or text == "how" or text == "howse" or text == "Howe":
                    text = "house"
                elif text == "military UAV" or text == "military UAB" or text == "military UAP" or text == "military uiv" or text == "military uave":
                    text = "military_UAV"
                elif text == "mini quadrocopter" or text == "mini quadro copter" or text == "mini quadcopter" or text == "mini quad copter" or text == "mini quadricopter" or text == "mini quadrocopter" or text == "Mini quadralcopter" or text == "Mini quoadracopter":
                    text = "mini_quadrocopter"
                elif text == "mosques" or text == "moscue" or text == "Moscow" or text == "mosqueue":
                    text = "mosque"
                elif text == "motorcycles" or text == "cycle" or text == "motor cycle":
                    text = "motorcycle"
                elif text == "persons" or text == "Parson" or text == "percent" or text == "Pearson" or text == "Carson":
                    text = "person"
                elif text == "c" or text == "see" or text == "Sia" or text == "see you" or text == "see ya" or text == "Co":
                    text = "sea"
                elif text == "sheeps" or text == "cheap" or text == "keep" or text == "Jeep" or text == "jeep":
                    text = "sheep"
                elif text == "ships" or text == "chip" or text == "chips" or text == "trip":
                    text = "ship"
                elif text == "sky tower" or text == "guy tower" or text == "guitar Tower" or text == "kightower" or text == "Sky Tower":
                    text = "skytower"
                elif text == "stadiums" or text == "Stadium":
                    text = "stadium"
                elif text == "submarines" or text == "sub marine" or text == "sub marines" or text == "submarin" or text == "the Marine" or text == "stop Marine":
                    text = "submarine"
                elif text == "suitcases" or text == "switch case" or text == "sweet case" or text == "sweet Chase" or text == "sweet case" or text == "Swift case":
                    text = "suitcase"
                elif text == "traffic light" or text == "perfect lights" or text == "epic lights" or text == "traffic lights":
                    text = "traffic_light"
                elif text == "traffic sign" or text == "perfect sign" or text == "epic sign" or text == "topic sign" or text == "perfect time":
                    text = "traffic_sign"
                elif text == "trains" or text == "brain" or text == "rain" or text == "Terrain" or text == "terrain":
                    text = "train"
                elif text == "three" or text == "sorry" or text == "3" or text == "free":
                    text = "tree"
                elif text == "trucks" or text == "track" or text == "Croc" or text == "crock":
                    text = "truck"
                elif text == "umbrellas":
                    text = "umbrella"
                elif text == "when" or text == "one":
                    text = "van"
                elif text == "yachts" or text == "yah" or text == "ya" or text == "yeah" or text == "yak" or text == "yard":
                    text = "yacht"
                return text
            except:
                return None


def select_class_by_voice(key):
    class_to_id = {value: key for (key, value) in cfg.id_to_class.items()}
    voice_input = VoiceInput()  # Main object
    try:
        class_name = voice_input.get_audio()
        #print(str(class_name) + "class name check " + str(type(class_name)))
        selected_class_id = class_to_id[class_name]
        print(class_name, selected_class_id)
        return selected_class_id
    except KeyError:
        return None