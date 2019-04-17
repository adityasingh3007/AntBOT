"""
  * Team Id : 288
  * Author List : Aditya Kumar Singh
  * Filename: path_planning.py
  * Theme: AntBOT
  * Functions: get_path(SIMs)  
  * Global Variables: Planning (object)
"""

"""
  * Class Name: Planning
  * Member(s): service_order, path, service_location, SIMs, Antbot
  * Functions: __init__(self,bin_id), store_service_location(self,service), decide_serving_order(self,SIMs),  decide_path(self),
               go_to_start(self,start), get_led_color(self,service), service(self,AH_num,start), execute_path(self,path)
  * Example for Object Creation: Planning()
"""
class Planning:
    service_order=False                                #To store the service order in which ANT hills are to be served
    path=""                                            #To store the path planning in string format
    service_location=False                             #To store the Shrubs Area configuration
    SIMs=False                                         #To store the details of all the SIMs
    Antbot={                                                # This tracks whether in each ant hill, its service location is serviced or not
        0 : [0,0],                                          #    once it is serviced, the corresponding element is made 1.
        1 : [0,0],
        2 : [0,0],
        3 : [0,0],
        }
        
    """
         Construction function for the class
    """
    def __init__(self):
        self.service_order=[]
        self.path=""
        self.service_location=False
    
    """
        * Function Name: store_service_location
        * Input: List having shrubs area congifuration starting from SA1 position
        * Output: none
        * Logic: This function accepts the SA configuration and stores it for further processing.
        * Example Call: store_service_location(["Honey Dew", "Leaves", "Wood", "Honey Dew", "Leaves", "Wood"])
    """     
    def store_service_location(self,service):
        self.service_location=service
    
    """
        * Function Name: decide_serving_order
        * Input: List having SIMs details in it
        * Output: none
        * Logic: This function accepts the 4 SIMs details and then decides what should be the order of servicing ANT Hills so as to minimize
                 the total time. The priority of ANT Hill as as Follows QAH > AH with only Trash removal > AH with Supply and Trash Removal >
                 AH with both supply requirement. Also say if after servicing a particular AH, BOT stopped at that AH itself. Now from there
                 if next AH to serviced is having a supply and Trash, then if the next AH is just opposite to the current one, AH will remove Trash
                 first and then give supply or else it will take supply and then remove Trash.  
        * Example Call: decide_serving_order(SIMs)
    """  
    def decide_serving_order(self,SIMs):
        self.SIMs=SIMs                                                    #Store the SIMs details first
        QAH=-1                                                            #To track whether QAH is present or not.
        AH_point=[0, 0, 0, 0]                                             #Point for AH, based on points only servicing order will be decided 
        for x in range(0,4):
            i=SIMs[x]                                                     #Get the current SIM details
            if(i.AH_type=="QAH"):                                         #If QAH is there, update the variable
                QAH=x
                """
                These conditions check that if opposite AH requires Trash then increse the points
                """
                if x==0 and SIMs[3].TR_req=="Required":               # AH0 and AH3 are opposite to each other
                   AH_point[3]+=3
                if x==3 and SIMs[0].TR_req=="Required":
                   AH_point[0]+=3
                if x==1 and SIMs[2].TR_req=="Required":               # AH1 and AH2 are opposite to each other
                   AH_point[2]+=3
                if x==2 and SIMs[1].TR_req=="Required":
                   AH_point[1]+=3  
            """
            Now deciding the point based on service conditions.
                # S     T 
                
                NOTE: The first one denotes Service Area 1, Second one Service Area 2 and 'S' means Servic, 'T' means Trash, 'X' means Nothing      
            """
            if(i.Serv_2_req!="No Supply Required" and i.Serv_1_req!="No Supply Required"):
                # S     S
                AH_point[x]+=2
            elif((i.Serv_2_req=="No Supply Required" and i.Serv_1_req!="No Supply Required") or (i.Serv_2_req!="No Supply Required" and i.Serv_1_req=="No Supply Required")) and i.TR_req=="Not Required":
                # S     X
                # X     S
                AH_point[x]+=5
            elif((i.Serv_2_req=="No Supply Required" and i.Serv_1_req!="No Supply Required") or (i.Serv_2_req!="No Supply Required" and i.Serv_1_req=="No Supply Required")) and i.TR_req=="Required":
                # S     T
                # T     S
                AH_point[x]+=10
            elif(i.Serv_2_req=="No Supply Required" and i.Serv_1_req=="No Supply Required" and i.TR_req!="Not Required"):
                # T     X
                # X     T
                AH_point[x]+=15
            elif(i.Serv_2_req=="No Supply Required" and i.Serv_1_req=="No Supply Required" and i.TR_req=="Not Required"):
                 # X     X
                 AH_point[x]+=20
        #print(AH_point)
        sorted_AH_point=sorted(AH_point,reverse=True,key=int)                            #Sort the points in descending order
        hist_index=[]
        #Now I have the descending points, but the AH numbers need to be changed according to points, so this will do that.
        #According to the points, it will rearrange all the AHs.  
        for i in range(0,4):
            val=sorted_AH_point[i]
            index=False
            for k in range(0,4):
                j=AH_point[k]
                if j==val and k not in hist_index:
                    index=k
                    hist_index.append(k)
                    break
            self.service_order.append(index)
        #If QAH is present, without worrying about the points, bring QAH to front
        if(QAH!=-1):
            for i in range(0,4):
                if(self.service_order[i]==QAH):
                    self.service_order.insert(0, self.service_order.pop(i))
                    break
        #print("Order: ")
        #print(self.service_order)
        
    """
        * Function Name: decide_path
        * Input: List having SIMs details in it
        * Output: none
        * Logic: This function starts servicing the AH one at a time according to the AH_num stored in service_order  
        * Example Call: decide_path()
    """
    def decide_path(self):
        path=""
        start="s"                                                               #For the First run, definitley BTO will be at start position, so start='s'
        for i in self.service_order:                      
            #print("")
            #print("\t\t\tGoing to service Ant Hill Number " + str(i))
            start=self.service(i,start)                                         #Get the path required to service the ANT Hill
        #After servicing all the AHs, this will bring BOT back to start position.
        self.go_to_start(start)
    
    """
        * Function Name: go_to_start
        * Input: Current position of BOT whether at Center Node ("c") or at some AH ("1" or "2" etc..) 
        * Output: none
        * Logic: This function starts servicing the AH one at a time according to the AH_num stored in service_order  
        * Example Call: go_to_start("c")
    """    
    def go_to_start(self,start):
        path=""
        if(start=="0"):
            path+="slsrss"
        elif(start=="3"):
            path+="srsrss"
        elif(start=="1"):
            path+="srslss"
        elif(start=="2"):
            path+="slslss"
        elif(start=="c"):
            path+="ss"
        self.execute_path(path)
    
    """
        * Function Name: get_led_color
        * Input: Service Requirement e.g. "Honey Dew"
        * Output: "R" or "G" or "B" depending upon the input
        * Logic: This function encodes the Service requirement into its colour so that RGB LED can be lighted up. 
        * Example Call: get_led_color("Honey Dew")
    """  
    def get_led_color(self,service):
        if(service=="Honey Dew"):
            return "R"
        elif(service=="Leaves"):
            return "G"
        elif(service=="Wood"):
            return "B" 
    
    """
        * Function Name: service
        * Input: AH number which is to be serviced, last position of BOT whether "s" or "c" or and AH num
        * Output: "c" or AH_num depending upon after servicing the current AH where the BOT exactly is.
        * Logic: This gives the path to service the given AH starting from the position which is given as arguement.
        * Example Call: service(0,"s")
    """ 
    def service(self,AH_num,start):
        path=""
        #Get the requirements of the current AH
        Serv1=self.SIMs[AH_num].Serv_1_req 
        Serv2=self.SIMs[AH_num].Serv_2_req
        Tr=self.SIMs[AH_num].TR_req
        #print("\t\t\t"+Serv1)
        #print("\t\t\t"+Serv2)
        #print("\t\t\t"+Tr)
        #print("")
        led= False
        """
        If start position of the BOT is "s" i.e from START NODE, then what commands to give, the below code does that.
        """
        if(start=="s"):
            #print("Starting from Start Node..")
            """
            If the AH need atleast one supply (doesnt caring about the Trash)
            """
            if(Serv1!="No Supply Required" and Serv2=="No Supply Required") or (Serv1=="No Supply Required" and Serv2!="No Supply Required"):
                if(Serv1!="No Supply Required"):
                    pos=self.service_location.index(Serv1)                #Get the position of it from the Shrubs area
                    led=self.get_led_color(Serv1)                         #Decide LED colour
                elif(Serv2!="No Supply Required"):
                    pos=self.service_location.index(Serv2)                #Get the position of it from the Shrubs area
                    led=self.get_led_color(Serv2)                         #Decide LED colour
                self.service_location[pos]="Empty"                        #Remove that element from the list. 
                com_turn=""
                if(pos<3):
                    com_turn="l"
                else:
                    com_turn="r"
                path+=com_turn
                if(pos==0 or pos==5):
                    path+="sss"
                elif(pos==1 or pos==4):
                    path+="ss"
                elif(pos==2 or pos==3):
                    path+="s"
                path+="b"+led;
                if(com_turn=="r"):
                    path+="qsrbsr"
                else:
                    path+="Qslbsl"
                if(pos==0 or pos==5):
                    path+="sss"
                elif(pos==1 or pos==4):
                    path+="ss"
                elif(pos==2 or pos==3):
                    path+="s"
                path+=com_turn+"s"
                if(AH_num==0 or AH_num==3):
                    path+="ls"
                    if(AH_num==0):
                        path+="rs"
                    else:
                        path+="ls"
                elif(AH_num==1 or AH_num==2):
                    path+="rs"
                    if(AH_num==1):
                        path+="ls"
                    else:
                        path+="rs"
                if(Serv1!="No Supply Required"):
                    path+="bw"
                    self.Antbot[AH_num][0]=1
                else:
                    path+="bW"
                    self.Antbot[AH_num][1]=1
                self.execute_path(path)
                #print("Now thinking required.....")
                path=""
                #Now if Trash is Required then what to do"
                if(Tr=="Required"):
                    if(Serv1=="No Supply Required"):
                        path+="sYbtos"
                        self.Antbot[AH_num][0]=1
                    else:
                        path+="sYbTos"
                        self.Antbot[AH_num][1]=1
                    if(AH_num==0 or AH_num==2):
                        path+="ls"
                        if(AH_num==0):
                            path+="l"
                        else:
                            path+="r"
                    else:
                        path+="rs"
                        if(AH_num==3):
                            path+="l"
                        else:
                            path+="r"
                    path+="spsos"
                    self.execute_path(path)
                    #print("\nServicing current ANT HIll is finished...")
                    #print("Now thinking required")
                    return "c"
                else:
                    path+="o"
                    if(Serv1=="No Supply Required"):
                        self.Antbot[AH_num][0]=1
                    else:
                        self.Antbot[AH_num][1]=1
                    self.execute_path(path)
                    #print("\nServicing current ANT HIll is finished...")
                    #print("Now thinking required...")
                    led=False
                    return str(AH_num)
            #If both position requires supplies
            elif(Serv1!="No Supply Required" and Serv2!="No Supply Required"):
                i=1
                while(i<=2):
                    if(i==1):
                        #Servicing pos 1
                        pos=self.service_location.index(Serv1)
                        led=self.get_led_color(Serv1)
                    else:
                        #Servicing pos 2
                        pos=self.service_location.index(Serv2)
                        led=self.get_led_color(Serv2)
                    self.service_location[pos]="Empty"
                    com_turn=""
                    turn=""
                    if(pos<3):
                        com_turn="l"
                        if(i==1):
                            turn="l"
                        else:
                            turn="r"
                    else:
                        com_turn="r"
                        if(i==1):
                            turn="r"
                        else:
                            turn="l"
                    if(i==1):
                        path+=com_turn
                    else:
                        path+=turn
                    if(pos==0 or pos==5):
                        path+="sss"
                    elif(pos==1 or pos==4):
                        path+="ss"
                    elif(pos==2 or pos==3):
                        path+="s"
                    path+="b"+led
                    if(i==1):
                        if(com_turn=="r"):
                            path+="qsrbsr"
                        else:
                            path+="Qslbsl"
                    else:
                        if(turn=="l"):
                            path+="qsrbsr"
                        else:
                            path+="Qslbsl"
                    if(pos==0 or pos==5):
                        path+="sss"
                    elif(pos==1 or pos==4):
                        path+="ss"
                    elif(pos==2 or pos==3):
                        path+="s"
                    path+=com_turn+"s"
                    if(AH_num==0 or AH_num==3):
                        path+="ls"
                        if(AH_num==0):
                            path+="rs"
                        else:
                            path+="ls"
                    elif(AH_num==1 or AH_num==2):
                        path+="rs"
                        if(AH_num==1):
                            path+="ls"
                        else:
                            path+="rs"
                    if(i==1):
                        path+="bwo"
                        self.Antbot[AH_num][0]=1
                    else:
                        path+="bWo"
                        self.Antbot[AH_num][1]=1
                    if(i==1):
                        path+="s"
                        if(AH_num==0 or AH_num==2):
                            path+="ls"
                            if(AH_num==0):
                                path+="rs"
                            else:
                                path+="ls"
                        elif(AH_num==1 or AH_num==3):
                            path+="rs"
                            if(AH_num==1):
                                path+="ls"
                            else:
                                path+="rs"                        
                    i+=1
                self.execute_path(path)
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required...")
                return str(AH_num)
            elif(Serv1=="No Supply Required" and Serv2=="No Supply Required") and Tr=="Required":
                """
                If both has No supply but Trash is needed to be removed
                This is a special case since we dont know where trash is kept, so we will take help of 
                picam to see where Trash is and then pick the trash. So for this g command is added.
                """
                path+="s"
                if(AH_num==0 or AH_num==3):
                    path+="ls"
                    if(AH_num==0):
                        path+="rs"
                    else:
                        path+="ls"
                else:
                    path+="rs"
                    if(AH_num==2):
                        path+="rs"
                    else:
                        path+="ls"
                path+="bYgo"
                self.execute_path(path)
                path=""
                if(AH_num==0 or AH_num==2):
                    path+="ls"
                    if(AH_num==0):
                        path+="ls"
                    else:
                        path+="rs"
                else:
                    path+="rs"
                    if(AH_num==3):
                        path+="ls"
                    else:
                        path+="rs"
                path+="psos"
                self.Antbot[AH_num][0]=1
                self.Antbot[AH_num][1]=1
                self.execute_path(path)
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required...")
                return "c"
            elif(Serv1=="No Supply Required" and Serv2=="No Supply Required") and Tr=="Not Required":
                """
                If nothing is required. Not even trash
                """
                self.Antbot[AH_num][0]=1
                self.Antbot[AH_num][1]=1
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required...")
                return "s"
        elif(start=="0" or start=="1" or start=="2" or start=="3"):
            """
            If BOT starts from any on the AH
            """
            #print("Starting from ant hill "+start)
            start=int(start)
            if(Tr=="Required"):                                        
                if(Serv1=="No Supply Required" and Serv2=="No Supply Required"):
                    path+="s"
                    if(start==0):
                        if(AH_num==1):
                            path+="lsslsbYgo"
                        elif(AH_num==2):
                            path+="lssrsbYgo"
                        elif(AH_num==3):
                            path+="sbYgo"
                    elif(start==1):
                        if(AH_num==0):
                            path+="rssrsbYgo"
                        elif(AH_num==2):
                            path+="sYg"
                        elif(AH_num==3):
                            path+="rsslsbYgo"
                    elif(start==2):
                        if(AH_num==0):
                            path+="lsslsbYgo"
                        elif(AH_num==1):
                            path+="sbYgo"
                        elif(Ah_num==3):
                            path+="lssrsbYgo"
                    elif(start==3):
                        if(AH_num==0):
                            path+="sbYgo"
                        elif(AH_num==1):
                            path+="rsslsbYgo"
                        elif(Ah_num==2):
                            path+="rssrsbYgo"
                    self.execute_path(path)
                    path="s"
                    if(AH_num==0 or AH_num==2):
                        path+="ls"
                        if(AH_num==0):
                            path+="ls"
                        else:
                            path+="rs"
                    else:
                        path+="rs"
                        if(AH_num==3):
                            path+="ls"
                        else:
                            path+="rs"
                    path+="psos"
                    self.Antbot[AH_num][0]=1
                    self.Antbot[AH_num][1]=1
                    self.execute_path(path)
                    #print("\nServicing current ANT HIll is finished...")
                    #print("Now thinking required...")
                    return "c"
                elif(Serv1!="No Supply Required" and Serv2=="No Supply Required")or(Serv1=="No Supply Required" and Serv2!="No Supply Required"):
                    """
                     Here if Supply is there and as well Trash, so if next AH is opposite to it, then take Trash first or else give supply first
                    """
                    if(start==0 and AH_num==3)or(start==3 and AH_num==0)or(start==1 and AH_num==2)or(start==2 and AH_num==1):
                        path+="ss"
                        if(Serv1=="No Supply Required"):
                            path+="bYtos"
                            self.Antbot[AH_num][0]=1
                        else:
                            path+="bYTos"
                            self.Antbot[AH_num][1]=1
                        if(AH_num==0 or AH_num==2):
                            path+="ls"
                            if(AH_num==0):
                                path+="ls"
                            else:
                                path+="rs"
                        else:
                            path+="rs"
                            if(AH_num==3):
                                path+="ls"
                            else:
                                path+="rs"
                        path+="pos"
                        self.execute_path(path)
                        print("Now thinking...")
                        path=""
                        if(Serv1!="No Supply Required"):
                            led=self.get_led_color(Serv1)
                            pos=self.service_location.index(Serv1)
                        elif(Serv2!="No Supply Required"):
                            led=self.get_led_color(Serv2)
                            pos=self.service_location.index(Serv2)
                        self.service_location[pos]="Empty"
                        path+="s"
                        com_turn=""
                        turn=""
                        if(pos<3):
                            com_turn="l"
                            turn="r"
                        else:
                            com_turn="r"
                            turn="l"
                        path+=turn
                        if(pos==0 or pos==5):
                            path+="sss"
                        elif(pos==1 or pos==4):
                            path+="ss"
                        elif(pos==2 or pos==3):
                            path+="s"
                        path+="b"+led
                        if(turn=="l"):
                            path+="qsrbsr"
                        else:
                            path+="Qslbsl"
                        if(pos==0 or pos==5):
                            path+="sss"
                        elif(pos==1 or pos==4):
                            path+="ss"
                        elif(pos==2 or pos==3):
                            path+="s"
                        path+=com_turn+"s"
                        if(AH_num==0 or AH_num==3):
                            path+="ls"
                            if(AH_num==0):
                                path+="rs"
                            else:
                                path+="ls"
                        elif(AH_num==1 or AH_num==2):
                            path+="rs"
                            if(AH_num==1):
                                path+="ls"
                            else:
                                path+="rs"
                        if(Serv1!="No Supply Required"):
                            path+="bwo"
                            self.Antbot[AH_num][0]=1
                        else:
                            path+="bWo"
                            self.Antbot[AH_num][1]=1
                        self.execute_path(path)
                        #print("\nServicing current ANT HIll is finished...")
                        #print("Now thinking required.....")
                        return str(AH_num)
                    else:
                        path+="s"
                        if(start==0 or start==2):
                            path+="ls"
                            if(start==0):
                                path+="r"
                            else:
                                path+="l"
                        else:
                            path+="rs"
                            if(start==3):
                                path+="r"
                            else:
                                path+="l"
                        self.execute_path(path)
                        ret=self.service(AH_num,"c")
                        return "c"
                    
            elif(Serv1=="No Supply Required" and Serv2=="No Supply Required"):
                self.Antbot[AH_num][0]=1
                self.Antbot[AH_num][1]=1
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required.....")
                return str(start)
            
            elif(Serv1!="No Supply Required" and Serv2!="No Supply Required")or(Serv1!="No Supply Required" and Serv2=="No Supply Required")or(Serv1=="No Supply Required" and Serv2!="No Supply Required"):
                path+="s"
                if(start==0 or start==2):
                    path+="ls"
                    if(start==0):
                        path+="r"
                    else:
                        path+="l"
                else:
                    path+="rs"
                    if(start==3):
                        path+="r"
                    else:
                        path+="l"
                self.execute_path(path)
                ret=self.service(AH_num,"c")
                return str(AH_num)            
        elif(start=="c"):
            """
            If BOT starts from center node (this case will come when BOT removed trash from the previous ANT hill.
            """
            #print("Starting from center Node....")
            if((Serv1=="No Supply Required" and Serv2=="No Supply Required")and Tr=="Required"):
                if(AH_num==0 or AH_num==3):
                    path+="rs"
                    if(AH_num==0):
                        path+="rs"
                    else:
                        path+="ls"
                else:
                    path+="ls"
                    if(AH_num==2):
                        path+="rs"
                    else:
                        path+="ls"
                path+="bYgo"
                self.execute_path(path)
                self.Antbot[AH_num][0]=1
                self.Antbot[AH_num][1]=1
                path=""
                if(AH_num==0 or AH_num==2):
                    path+="ls"
                    if(AH_num==0):
                        path+="ls"
                    else:
                        path+="rs"
                else:
                    path+="rs"
                    if(AH_num==3):
                        path+="ls"
                    else:
                        path+="rs"
                path+="pos"
                self.execute_path(path)
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required...")
                return "c"
            
            elif((Serv1=="No Supply Required" and Serv2=="No Supply Required")and Tr=="Not Required"):
                self.Antbot[AH_num][0]=1
                self.Antbot[AH_num][1]=1
                #print("\nServicing current ANT HIll is finished...")
                #print("Now thinking required...")
                return "c"
                
            elif(Serv1!="No Supply Required" and Serv2=="No Supply Required") or (Serv1=="No Supply Required" and Serv2!="No Supply Required"):
                if(Serv1!="No Supply Required"):
                    led=self.get_led_color(Serv1)
                    pos=self.service_location.index(Serv1)
                elif(Serv2!="No Supply Required"):
                    led=self.get_led_color(Serv2)
                    pos=self.service_location.index(Serv2)
                self.service_location[pos]="Empty"
                path+="s"
                com_turn=""
                turn=""
                if(pos<3):
                    com_turn="l"
                    turn="r"
                else:
                    com_turn="r"
                    turn="l"
                path+=turn
                if(pos==0 or pos==5):
                    path+="sss"
                elif(pos==1 or pos==4):
                    path+="ss"
                elif(pos==2 or pos==3):
                    path+="s"
                path+="b"+led
                if(turn=="l"):
                    path+="qsrbsr"
                else:
                    path+="Qslbsl"
                if(pos==0 or pos==5):
                    path+="sss"
                elif(pos==1 or pos==4):
                    path+="ss"
                elif(pos==2 or pos==3):
                    path+="s"
                path+=com_turn+"s"
                if(AH_num==0 or AH_num==3):
                    path+="ls"
                    if(AH_num==0):
                        path+="rs"
                    else:
                        path+="ls"
                elif(AH_num==1 or AH_num==2):
                    path+="rs"
                    if(AH_num==1):
                        path+="ls"
                    else:
                        path+="rs"
                if(Serv1!="No Supply Required"):
                    path+="bw"
                    self.Antbot[AH_num][0]=1
                else:
                    path+="bW"
                    self.Antbot[AH_num][1]=1
                self.execute_path(path)
                #print("Now thinking required.....")
                path=""
                if(Tr=="Required"):
                    if(Serv1=="No Supply Required"):
                        path+="sYbtos"
                        self.Antbot[AH_num][0]=1
                    else:
                        path+="sYbTos"
                        self.Antbot[AH_num][1]=1
                    if(AH_num==0 or AH_num==2):
                        path+="ls"
                        if(AH_num==0):
                            path+="l"
                        else:
                            path+="r"
                    else:
                        path+="rs"
                        if(AH_num==3):
                            path+="l"
                        else:
                            path+="r"
                    path+="spsos"
                    self.execute_path(path)
                    #print("\nServicing current ANT HIll is finished...")
                    #print("Now thinking required")
                    return "c"
                else:
                    path+="o"
                    if(Serv1=="No Supply Required"):
                        self.Antbot[AH_num][0]=1
                    else:
                        self.Antbot[AH_num][1]=1
                    self.execute_path(path)
                    #print("\nServicing current ANT HIll is finished...")
                    #print("Now thinking required...")
                    return str(AH_num)

            elif(Serv1!="No Supply Required" and Serv2!="No Supply Required"):
                i=1
                path+="s"
                while(i<=2):
                    if(i==1):
                        #Servicing pos 1
                        led=self.get_led_color(Serv1)
                        pos=self.service_location.index(Serv1)
                    else:
                        #Servicing pos 2
                        led=self.get_led_color(Serv2)
                        pos=self.service_location.index(Serv2)
                    self.service_location[pos]="Empty"
                    com_turn=""
                    turn=""
                    if(pos<3):
                        com_turn="l"
                        turn="r"
                    else:
                        com_turn="r"
                        turn="l"
                    path+=turn
                    if(pos==0 or pos==5):
                        path+="sss"
                    elif(pos==1 or pos==4):
                        path+="ss"
                    elif(pos==2 or pos==3):
                        path+="s"
                    path+="b"+led
                    if(turn=="l"):
                        path+="qsrbsr"
                    else:
                        path+="Qslbsl"
                    if(pos==0 or pos==5):
                        path+="sss"
                    elif(pos==1 or pos==4):
                        path+="ss"
                    elif(pos==2 or pos==3):
                        path+="s"
                    path+=com_turn+"s"
                    if(AH_num==0 or AH_num==3):
                        path+="ls"
                        if(AH_num==0):
                            path+="rs"
                        else:
                            path+="ls"
                    elif(AH_num==1 or AH_num==2):
                        path+="rs"
                        if(AH_num==1):
                            path+="ls"
                        else:
                            path+="rs"
                    if(i==1):
                        path+="bwo"
                        self.Antbot[AH_num][0]=1
                    else:
                        path+="bWo"
                        self.Antbot[AH_num][1]=1
                    if(i==1):
                        path+="s"
                        if(AH_num==0 or AH_num==2):
                            path+="ls"
                            if(AH_num==0):
                                path+="rs"
                            else:
                                path+="ls"
                        elif(AH_num==1 or AH_num==3):
                            path+="rs"
                            if(AH_num==1):
                                path+="ls"
                            else:
                                path+="rs"
                    else:
                        x=1
                        #print("\nServicing current ANT HIll is finished...")
                        #print("Now thinking required...")
                    i+=1
                self.execute_path(path)
                return str(AH_num)
    """
        * Function Name: execute_path(self,path)
        * Input: Path for servicing a AH
        * Output: none
        * Logic: This function adds the path for each AH to a main path variable. 
        * Example Call: execute_path("sslslbYslu")
    """           
    def execute_path(self,path):
        #print(path)
        #print(len(path))
        self.path+=path
        #print(self.Antbot)
                   
#Creating object
Plan=Planning()

"""
  * Function Name: execute_path(self,path)
  * Input: All SIMs details
  * Output: the complete path
  * Logic: This function calls the various functions in order to execute path planning and in the end returns a path variable having
           complete command in it.
  * Example Call: execute_path("sslslbYslu")
""" 
def get_path(SIMs):
    Plan.decide_serving_order(SIMs)
    Plan.decide_path()
    return Plan.path
