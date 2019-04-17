"""
  * Team Id : 288
  * Author List : Aditya Kumar Singh
  * Filename: SIM_Decoding.py
  * Theme: AntBOT
  * Functions: show_details(object), standardize_aruco_id_binary(int[base:2]),
               decode_SIM(int), extract_full_details(list)
  * Global Variables: None
"""

"""
  * Class Name: SIM_details
  * Member(s): ID, AH_type, AH_num, Serv_2_req, Serv_1_req, TR_req
  * Functions: __init__(self,bin_id), find_AH_type(self,bin_id), find_AH_num(self,bin_id), find_Serv_2_req(self,bin_id),
               find_Serv_1_req(self,bin_id), find_TR_req(self,bin_id)
  * Example for Object Creation: SIM_details()
"""
class SIM_details:
    ID=""                                               #To store the id of the Aruco
    AH_type=""
    AH_num=""
    #Note: Serv stands for Service and req stands for requirement
    Serv_2_req=""
    Serv_1_req=""
    TR_req=""
    
    """
         Construction function for the class
    """
    def __init__(self,bin_id):
        self.ID=str(int(bin_id,2))
        self.AH_type=False
        self.AH_num=False
        self.Serv_2_req=False
        self.Ser_1_req=False
        self.TR_req=False
    
    """
        * Function Name: find_AH_type
        * Input: None
        * Output: none
        * Logic: This function will find the type of ANT HILL based on the 7th bit of the ID passed
                 and then store it in AH_type variable
        * Example Call: SIM_details.find_AH_type("01101101")
    """ 
    def find_AH_type(self,bin_id):
        if bin_id[0]=="0":
            self.AH_type="RAH"
        else:
            self.AH_type="QAH"
    
    """
        * Function Name: find_AH_num
        * Input: None
        * Output: none
        * Logic: This function will find the ANT HILL number  based on the 6th and 5th bit of the ID passed
                 and then store it in AH_num variable
        * Example Call: SIM_details.find_AH_num("01101101")
    """ 
    def find_AH_num(self,bin_id):
        bit_6_5=bin_id[1:3]
        if bit_6_5=="00":
            self.AH_num="0"
        elif bit_6_5=="01":
            self.AH_num="1"
        elif bit_6_5=="10":
            self.AH_num="2"
        elif bit_6_5=="11":
            self.AH_num="3"

    """
        * Function Name: find_Serv_2_req
        * Input: None
        * Output: none
        * Logic: This function will find the service requirement at location 2 based on the 4th and 3th bit of the ID passed
                 and then store it in Serv_2_req variable
        * Example Call: SIM_details.find_Serv_2_req("01101101")
    """ 
    def find_Serv_2_req(self,bin_id):
        bit_4_3=bin_id[3:5]
        if bit_4_3=="00":
            self.Serv_2_req="No Supply Required"
        elif bit_4_3=="01":
            self.Serv_2_req="Honey Dew"
        elif bit_4_3=="10":
            self.Serv_2_req="Leaves"
        elif bit_4_3=="11":
            self.Serv_2_req="Wood"
    
    """
        * Function Name: find_Serv_1_req
        * Input: None
        * Output: none
        * Logic: This function will find the service requirement at location 1 based on the 2nd and 1st bit of the ID passed
                 and then store it in Serv_1_req variable
        * Example Call: SIM_details.find_Serv_1_req("01101101")
    """ 
    def find_Serv_1_req(self,bin_id):
        bit_2_1=bin_id[5:7]
        if bit_2_1=="00":
            self.Serv_1_req="No Supply Required"
        elif bit_2_1=="01":
            self.Serv_1_req="Honey Dew"
        elif bit_2_1=="10":
            self.Serv_1_req="Leaves"
        elif bit_2_1=="11":
            self.Serv_1_req="Wood"
    
    """
        * Function Name: find_TR_req
        * Input: None
        * Output: none
        * Logic: This function will find the Trash requirement based on the 0th bit of the ID passed
                 and then store it in TR_req variable
        * Example Call: SIM_details.find_TR_req("01101101")
    """ 
    def find_TR_req(self,bin_id):
        if bin_id[7]=="1":
            self.TR_req="Required"
        else:
            self.TR_req="Not Required"

"""
  * Function Name: show_details
  * Input: object of SIM_details class
  * Output: none
  * Logic: This function will print all the SIM details on the screen
  * Example Call: show_details(SIM)
""" 
def show_details(SIM):
        print("The details are as follows:-")
        print("\tID: "+ SIM.ID)
        print("\tAH Type: "+SIM.AH_type)
        print("\tAH Number: "+SIM.AH_num)
        print("\tSer 2 Requirement: "+SIM.Serv_2_req)
        print("\tSer 1 Requirement: "+SIM.Serv_1_req)
        print("\tTrash Removal Required: "+SIM.TR_req)


"""
  * Function Name: standardize_aruco_id_binary
  * Input: object of SIM_details class
  * Output: return binary number after removing 0b and adding necessary 0 infront in order to make it 8 bit number.
  * Logic: This function will remove "0b" from the binary converted ID since we dont need that for further processing. 
  * Example Call: standardize_aruco_id_binary("0b10101101")
""" 
def standardize_aruco_id_binary(bin_num):
    bin_num=(bin_num[2:len(bin_num)])
    if len(bin_num)!=8:
        for i in range(len(bin_num),8):
            bin_num="0"+bin_num
    return bin_num

"""
  * Function Name: decode_SIM
  * Input: aruco id in binary form
  * Output: returns the decoded information of the id passed(in binary form) as an object. 
  * Logic: This function will process the id and find out all the details and then return it in object form
  * Example Call: decode_SIM("10110101"):
""" 
def decode_SIM(_id):
    data=SIM_details(_id)
    data.find_AH_type(_id)
    data.find_AH_num(_id)
    data.find_Serv_2_req(_id)
    data.find_Serv_1_req(_id)
    data.find_TR_req(_id)
    #show_details(_id)
    return data

"""
  * Function Name: extract_full_details
  * Input: complete aruco id list (in decimal form)
  * Output: returns the decoded information of the ids passed as a list objects. Each object is having the complete details
            of the id which was passed. 
  * Logic: This function will process the id list passed to it, convert it to binar form and the extract
           full details and store it as object as a member of my_SIMs list.
  * Example Call: extract_full_details([56,4,194,121])
""" 
def extract_full_details(id_list):
    my_SIMs=[]
    for x in id_list:
        aruco_id_bin=(bin)(x)
        my_SIMs.append(decode_SIM(standardize_aruco_id_binary(aruco_id_bin)))
    """
    #For printing all the detials
    for x in my_SIMs:
        show_details(x)
    """    
    return my_SIMs

aruco_id=[210,32,17,120]
x=extract_full_details(aruco_id)
for i in x:
    show_details(i)

