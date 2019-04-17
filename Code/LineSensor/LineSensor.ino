/*
 ▪ Team Id: 288
 ▪ Author List: Aditya Kumar Singh, Karthik S.
 ▪ Filename: LineSensor.ino
 ▪ Theme: AntBOT
 ▪ Functions: ISR(RXC Complete), Base_servo(), turn_left(), turn_right(), move_back(), set_direction(char),
 Timer1_initiallise(), usart_init(void), USARTWriteChar(char), Serial_print(char[]), ADC_Init(),
 ADC_Read(unsigned char), main(void)
 ▪ Global Variables: char command, int aruco, int trash_count, int flag_two_node_stop, Servo_ SERVO 
 */

#include <avr/io.h>
#include<avr/interrupt.h>
#include<util/delay.h>
#include "ABservo.h"                                                               //Library to control SRERVOS attached to the BOT

/*
  LEFT Wheel(en1): 7(D7),8(B0),9   ::: RIGHT Wheel(en2): 10,11(B3),12(B4)
 Condition for forward: 8H,7L :: 11H, 12L
 */

#define en1 9
#define a1 8
#define a2 7
#define en2 10
#define b1 11
#define b2 12
#define threshold 29                                                              //Threshold value for the sensor. Calculated using [(B+W)/2) - B/3]

volatile char command = 'h';                                                      //Variable which will store the command received by Serial line
int aruco=0;                                                                      //Flag variable which will move the BOT automatically for arucos detection when 'z' is received
int trash_count = 0;                                                              //Flag variable to count number of times Trash placement is done on TDZ
int flag_two_node_stop = 1;                                                       //This variables makes the BOT stop when two of its sensor is on black

Servo_ SERVO;                                                                     //Object creation of class Servo_

//Function Prototypes
void Base_servo();
void turn_left();
void turn_right();
void move_back();
void set_direction(char);
void Timer1_initiallise();
void usart_init(void);
void USARTWriteChar(char data);
void Serial_print(char[]);
void ADC_Init();
unsigned char ADC_Read(unsigned char);
/*
 ▪ Function Name: ISR(USART_RX_vect)
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This is an Interrupt Service routine which will store the value coming on the serial line into the variable
 command.
 ▪ Example Call: Will be called automatically when data is available to be read from the serial line.
 */
ISR(USART_RX_vect) {
  command = UDR0;
}

/*
 ▪ Function Name: Base_servo()
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This function rotates the base servo with its OCR value as 37 ( little towards right ).
 ▪ Example Call: Base_servo()
 */
void Base_servo() {
  SERVO.base.turn(37);
}

/*
 ▪ Function Name: turn_right
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This function will turn the BOT right 90 degree.
 ▪ Example Call: turn_right()
 */
void turn_right() {
  int loop_ = 1;                                        //Flag variable to exit from loop
  uint8_t leftsensor, centersensor, rightsensor;        //Variables to store values from the sensor
  leftsensor = ADC_Read(0);
  centersensor = ADC_Read(1);
  rightsensor = ADC_Read(2);
  //Flag variables to store the hist_position of the sensors in boolean form( 0 for black, 1 for white)
  int hist_center = 0;
  int hist_right = 0;
  int flag_right = 0;

  //Maximum number of count the right sensor can change(from Black to white or vice versa) in order to complete a turn. 
  int flag_max_count = 0;

  //Setting the initial position for motors and accordingly the max_count value
  OCR1A = 65500;
  OCR1B = 35500;


  if (rightsensor >= threshold) {
    flag_max_count = 3;
  }
  else if (rightsensor < threshold) {
    flag_max_count = 2;
  }
  if (centersensor >= threshold) {
    hist_center = 0;
  }
  else if (centersensor < threshold) {
    hist_center = 1;
  }

  //From here BOT will start taking turn
  while (loop_) {
    //Read the sensor values
    centersensor = ADC_Read(1);
    rightsensor = ADC_Read(2);
    if (rightsensor >= threshold) {
      if (hist_right) {
        hist_right = 0;
        flag_right++;
      }
    }
    else if (rightsensor < threshold) {
      if (!hist_right) {
        hist_right = 1;
        flag_right++;
      }
    }
    if (centersensor >= threshold) {
      if (hist_center) {
        hist_center = 0;
      }
      if (flag_right >= flag_max_count) {
        //_delay_ms(10);
        OCR1A = 0;       //rotation complete
        OCR1B = 0;
        loop_ = 0;
      }
    }
    else if (centersensor < threshold) {
      if (!hist_center) {
        hist_center = 1;
      }
    }
  }
}

/*
 ▪ Function Name: turn_left
 ▪ Input: int _180 . This is a flag variable which will tell whether to take full 180 degree turn starting from the left of the bot 
 ▪ Output: None
 ▪ Logic: This function will turn the BOT left 90 degree or 180.
 ▪ Example Call: turn_left(1)
 */
void turn_left(int _180) {
  int loop_ = 1;                                        //Flag variable to exit from loop
  uint8_t leftsensor, centersensor, rightsensor;        //Variables to store values from the sensor
  leftsensor = ADC_Read(0);
  centersensor = ADC_Read(1);
  rightsensor = ADC_Read(2);
  //Flag variables to store the hist_position of the sensors in boolean form( 0 for black, 1 for white)
  int hist_center = 0;
  int hist_left = 0;
  int flag_left = 0;
  // variable to store the maximum number of changes left sensor it needs to make from black to white or vice versa in order to make a left turn 
  int flag_max_count = 0;
  // initialising the initial ocr values for both the motors
  OCR1A = 17500;
  OCR1B = 40500;
  if(_180) {
    PORTB &= ~(1 << PB0);        //Left
    PORTD |= (1 << PD7);

    PORTB |= (1 << PB3);
    PORTB &= ~(1 << PB4);

    //higher speed for making sure the bot rotates on the axis

    OCR1A = 60500;
    OCR1B = 45500;
  }
  if (leftsensor >= threshold) {
    flag_max_count = 3;
  }
  else if (leftsensor < threshold) {
    flag_max_count = 2;
  }
  if (centersensor >= threshold) {
    hist_center = 0;
  }
  else if (centersensor < threshold) {
    hist_center = 1;
  }
  // startes rotating
  while (loop_) {
    leftsensor = ADC_Read(0);
    centersensor = ADC_Read(1);
    if (leftsensor >= threshold) {
      if (hist_left) {
        hist_left = 0;
        flag_left++;
      }
    }
    else if (leftsensor < threshold) {
      if (!hist_left) {
        hist_left = 1;
        flag_left++;
      }
    }
    if (centersensor >= threshold) {
      if (hist_center) {
        hist_center = 0;
        if (flag_left >= flag_max_count) {
          OCR1A = 0;          // run over
          OCR1B = 0;          // run over
          loop_ = 0;         
          if(aruco==3) {      // in the initial run to give a command 's' after 'o' ( 180 ) degree to detect all the arucos this condition this there   
            command='s';
            aruco++;
          }
          else {
            command = 'n';     // else wait for the next command from pi 
          }
        }
      }
    }
    else if (centersensor < threshold) {
      if (!hist_center) {
        hist_center = 1;
      }
    }
  }
}


/*
 ▪ Function Name: move_back
 ▪ Input: None 
 ▪ Output: None
 ▪ Logic: This function will move back after aligning itself to the black line by coming a little forward
 ▪ Example Call: move_back()
 */


void move_back() {
  uint8_t leftsensor, centersensor, rightsensor;            //Variable to store the sensor values
  int i = 0;
  int straight = 1;   // flag variable to align to the black line before going back
  int str_count=0;    // variable to check number of times the center sensor is on the line before going back
  while (1)
  {
    //Read left, middle, right sensor value from 3 channel line sensor
    leftsensor = ADC_Read(2);
    centersensor = ADC_Read(1);
    rightsensor = ADC_Read(0);

    if (straight == 0)           // logic to go back by setting the ocr values of motors based on the position of the line sensors 
    {
      while (1)
      {
        leftsensor = ADC_Read(2);
        centersensor = ADC_Read(1);
        rightsensor = ADC_Read(0);
        if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor < threshold))
        {
          Serial_print("Straight");
          OCR1B = 50000;
          OCR1A = 32125;
        }
        else if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor > threshold))
        {
          Serial_print("Little Left");
          /*OCR1B = 42405;
           OCR1A = 26214;*/
          if ((centersensor > 2*threshold) || ( rightsensor > 2*threshold))
          {
            //Serial_print("little left stop");
            Serial_print("NODE");
            //_delay_ms(100);
            OCR1A = 0;
            OCR1B = 0;
            command = 'n';
            return;
          }
        }
        else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor < threshold))
        {
          Serial_print("little Right");
          /*OCR1B = 29298;
           OCR1A = 32125;*/
          if ((centersensor > 2*threshold) || ( leftsensor > 2*threshold))
          {
            //Serial_print("little right stop");
            Serial_print("NODE");
            //_delay_ms(100);
            OCR1A = 0;
            OCR1B = 0;
            command = 'n';
            return;
          }
        }
        else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor > threshold))
        {
          Serial_print("Left");
          //OCR1B = 20000;
          //OCR1A = 40125;
          OCR1B = 50000;
          OCR1A = 32125;
        }
        else if (( leftsensor > threshold) && (centersensor < threshold) && ( rightsensor < threshold))
        {
          Serial_print("Right");
          //OCR1B = 55000;
          //OCR1A = 20000;
          OCR1B = 50000;
          OCR1A = 32125;
        }
        else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor < threshold))
        {
          Serial_print("WHITE");
          OCR1B = 39321;
          OCR1A = 32125;
        }
        else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor > threshold))
        {
          Serial_print("NODE");
          OCR1A = 0;
          //_delay_ms(30);
          OCR1B = 0;
          command = 'n';
          return;
        }
      }
    }
    else if (straight == 1) {
      PORTB |= (1 << PB0);              //straight
      PORTD &= ~(1 << PD7);

      PORTB |= (1 << PB3);
      PORTB &= ~(1 << PB4);
    }
    while (straight ) {                //logic to go straight by setting the ocr values according to the line sensors  
      leftsensor = ADC_Read(0);
      centersensor = ADC_Read(1);
      rightsensor = ADC_Read(2);
      if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor < threshold))
      {
        Serial_print("Straight");
        OCR1A = 32125;
        OCR1B = 50000;
        str_count++;
        if(str_count>=20) {            //making it align for 20 times with the straight condition before going back
          straight = 0;
          _delay_ms(100);
          OCR1A = 0;
          OCR1B = 0;
          PORTB &= ~(1 << PB0);        //Back
          PORTD |= (1 << PD7);

          PORTB &= ~(1 << PB3);
          PORTB |= (1 << PB4);
          //_delay_ms(2000);
          Serial_print("st over");
          str_count=0;
          break;

        }
      }
      else if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor > threshold))
      {
        Serial_print("Little Left");
        OCR1A = 62125;
        OCR1B = 4598;
      }
      else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor < threshold))
      {
        Serial_print("little Right");
        OCR1A = 35214;
        OCR1B = 62405;
      }
      else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor > threshold))
      {
        Serial_print("left");
        OCR1A = 35980;
        OCR1B = 0;
      }
      else if (( leftsensor > threshold) && (centersensor < threshold) && ( rightsensor < threshold))
      {
        Serial_print("Right");
        OCR1A = 0;
        OCR1B = 45874;
      }
      else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor < threshold))
      {
        Serial_print("WHITE");
        OCR1A = 32125;
        OCR1B = 39321;
        straight = 0;                //time to go back !
        _delay_ms(100);
        OCR1A = 0;                   //stopping the motors
        OCR1B = 0;                   
        PORTB &= ~(1 << PB0);        //Back
        PORTD |= (1 << PD7);

        PORTB &= ~(1 << PB3);
        PORTB |= (1 << PB4);
        //_delay_ms(2000);
        Serial_print("st over");
        break;
      }
      else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor > threshold))
      {
        //do nothing
      }
    }

  }
}


/*
 ▪ Function Name: set_direction
 ▪ Input: direction_ -> char which will be used to set dirction of the motors
 ▪ Output: None
 ▪ Logic: This function will change the motor direction according to the character passed to it
 ▪ Example Call: set_direction('s')
 */
void set_direction(char direction_ ) {
  switch (direction_) {
  case 's': 
    PORTB |= (1 << PB0);        //Straight
    PORTD &= ~(1 << PD7);

    PORTB |= (1 << PB3);
    PORTB &= ~(1 << PB4);
    break;
  case 'r': 
    PORTB |= (1 << PB0);        //Right
    PORTD &= ~(1 << PD7);

    PORTB &= ~(1 << PB3);
    PORTB |= (1 << PB4);
    turn_right();
    command = 'n';
    break;
  case 'l': 
    PORTB &= ~(1 << PB0);        //Left
    PORTD |= (1 << PD7);

    PORTB |= (1 << PB3);
    PORTB &= ~(1 << PB4);
    turn_left(0);
    command='n';
    break;
  case 'b': 
    PORTB &= ~(1 << PB0);        //Back
    PORTD |= (1 << PD7);

    PORTB &= ~(1 << PB3);
    PORTB |= (1 << PB4);
    move_back();
    command = 'n';
    break;
  default: 
    PORTB &= ~(1 << PB0);        //Stop
    PORTD &= ~(1 << PD7);

    PORTB &= ~(1 << PB3);
    PORTB &= ~(1 << PB4);
    break;
  }
}


/*
 ▪ Function Name: Timer1_initiallise()
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This function will initiallise TIMER1 in Fast PWM Mode for both channels A and B.
 ▪ Example Call: Timer_initiallise()
 */
void Timer1_initiallise() {
  ICR1 = 0xFFFF;                                       //Setting TOP value as its maximum value
  //Initila duty cycle 0
  OCR1A = 0;
  OCR1B = 0;
  TCCR1A |= (1 << COM1A1) | (1 << COM1B1);             //Non-inverting mode
  //Fast PWM
  TCCR1A |= (1 << WGM11);
  TCCR1B |= (1 << WGM12) | (1 << WGM13);
  TCCR1B |= (1 << CS10);                               //Start the Timer with no prescaler
}

/*
 ▪ Function Name: usart_init()
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This function will initiallise UART with BAUD RATE 9600bps.
 ▪ Example Call: usart_init()
 */
void usart_init(void)
{
  UCSR0A = 0x00;                                      //Asynchronous
  UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);             //8 bit
  UBRR0L = 103;                                       //9600 Baud RAte
  UCSR0B = (1 << RXEN0) | (1 << TXEN0) | (1 << RXCIE0); //Enable RX and TX with Interrupt on RX Complete.
}

/*
 ▪ Function Name: USARTWriteChar
 ▪ Input: data -> character which is to be sent through UART.
 ▪ Output: None
 ▪ Logic: This function will send the data(character, passed to it) to UART.
 ▪ Example Call: USARTWriteChar('a')
 */
void USARTWriteChar(char data)
{
  while (!(UCSR0A & (1 << UDRE0)))        //Before writing, wait until buffer is empty
  {

  }
  UDR0 = data;                            //Write the data
}

/*
 ▪ Function Name: Serial_print
 ▪ Input: arr[] -> string which is meant to be printed on serial line.
 ▪ Output: None
 ▪ Logic: This function will read single character,add them in a string array and print it on the serial line with \n at the end.
 ▪ Example Call: Serial_print("Stopped")
 */
void Serial_print(char arr[100]) {
  for (int i = 0; arr[i] != '\0'; i++)
  {
    USARTWriteChar(arr[i]);
  }
  USARTWriteChar('\n');
}


/*
 ▪ Function Name: ADC_Init
 ▪ Input: None
 ▪ Output: None
 ▪ Logic: This function initiallises ADC.
 ▪ Example Call: ADC_Init()
 */
void ADC_Init()
{
  ADMUX = (1 << REFS0) | (1 << ADLAR);                      // Vref: Avcc, ADC channel: 0, Left Justified
  ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // ADC Enable, 128 Prescaler => Frequency_ADC = 125kHz
}

/*
 ▪ Function Name: ADC_Read
 ▪ Input: channel  -> unsigned char which stores the channel for which ADC
 will be performed.
 ▪ Output: uint8_t which holds the value after ADC value of any the channel was passed to the function.
 ▪ Logic: Perofrming logical AND between 0x07 and variable channel will give the original channel for which the
 ADC is to be performed. But during this process REF bits and ADLAR bits in ADMUX register will change.
 So,logical OR is applied to the above result and it is set back to intial value. After this, ADC starts and is made to wait
 untill conversion finishes. The conversion flag is manually cleared. After that the result is returned.
 ▪ Example Call: ADC_Read(0)
 */
uint8_t ADC_Read(unsigned char channel)
{
  ADMUX = (1 << REFS0) | (1 << ADLAR) | (channel & 0x07);   //Set input channel to read
  ADCSRA |= (1 << ADSC);                                    //Start ADC conversion
  while (!(ADCSRA & (1 << ADIF)));                          //Wait until end of conversion by polling ADC interrupt flag
  ADCSRA |= (1 << ADIF);                                    //Clear the interrupt flag manually
  return ADCH;                                              //Return ADC word
}

/*
 ▪ Function Name: main
 ▪ Input: void
 ▪ Output: int to inform the caller that the program exited correctly or
 incorrectly (C code standard)
 ▪ Logic: Initialises the Serial communcation with 9600 Baud Rate and calls
 ADC_Init to intiallise the ADC. Then under infinite loop,it calls ADC_Read
 with values 0, 1, 2 to read ADC value of channel 0, 1, 2 respectively.
 Post this, commands from pi are executed.
 ▪ Example Call: Called automatically by the Operating System.
 */
int main(void)
{

  uint8_t leftsensor, centersensor, rightsensor;            //Variable to store the sensor values
  //Making PORT as OUTPUT
  DDRD = 0xFF;
  DDRB = 0xFF;
  sei();                                                   //Enabling the global interrupts
  usart_init();               //Intitialize UART
  ADC_Init();                 //Initialize ADC       //Intiallise TIMER1
  Timer1_initiallise();
  Serial_print("lib");
  SERVO.grip._release();
  SERVO.arm.lift();
  while (1)
  {
    //Serial_print(TCNT0);
    //Read left, middle, right sensor value from 3 channel line sensor
    leftsensor = ADC_Read(0);
    centersensor = ADC_Read(1);
    rightsensor = ADC_Read(2);

    if (command == 's') {                       // command to go straight
      set_direction(command);
      if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor < threshold))
      {
        Serial_print("Main");
        Serial_print("Straight");
        OCR1A = 32125;
        OCR1B = 50000;
      }
      else if (( leftsensor < threshold) && (centersensor > threshold) && ( rightsensor > threshold))
      {
        Serial_print("little Left ");
        OCR1A = 65125;
        OCR1B = 45298;
        if ((centersensor > 2*threshold) && ( rightsensor > 2*threshold))
        {
          //Serial_print("little Left stop");
          Serial_print("NODE");
          _delay_ms(100);
          OCR1A = 0;
          OCR1B = 0;
          if(aruco==1) {
            command='s';
            aruco++;
          }
          else if(aruco==2) {
            command='o';
            aruco++;
          }
          else if (aruco==4) {
            command='s';
            aruco++;
          }
          else {
            set_direction('h');
            command = 'n';
          }
          //USARTWriteChar(48+aruco);
        }
      }
      else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor < threshold))
      {
        Serial_print("little Right");
        OCR1A = 35214;
        OCR1B = 65405;
        if ((centersensor > 2*threshold) && ( leftsensor > 2*threshold))
        {
          //Serial_print("little right stop");
          Serial_print("NODE");
          _delay_ms(100);
          OCR1A = 0;
          OCR1B = 0;
          if(aruco==1) {
            command='s';
            aruco++;
          }
          else if(aruco==2) {
            command='o';
            aruco++;
          }
          else if (aruco==4) {
            command='s';
            aruco++;
          }
          else {
            set_direction('h');
            command = 'n';
          }
          //USARTWriteChar(48+aruco);
        }
      }
      else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor > threshold))
      {
        Serial_print("left");
        OCR1A = 35980;
        OCR1B = 0;
      }
      else if (( leftsensor > threshold) && (centersensor < threshold) && ( rightsensor < threshold))
      {
        Serial_print("Right");
        OCR1A = 0;
        OCR1B = 45874;
      }
      else if (( leftsensor < threshold) && (centersensor < threshold) && ( rightsensor < threshold))
      {
        Serial_print("WHITE");
        OCR1A = 32125;
        OCR1B = 39321;
      }
      else if (( leftsensor > threshold) && (centersensor > threshold) && ( rightsensor > threshold))
      {
        Serial_print("NODE");
        OCR1A = 32125;
        OCR1B = 40000;
        _delay_ms(100);
        OCR1A = 0;
        OCR1B = 0;
        if(aruco==1) {
          command='s';
          aruco++;
        }
        else if(aruco==2) {
          command='o';
          aruco++;
        }
        else if (aruco==4) {
          command='s';
          aruco++;
        }
        else {
          set_direction('h');
          command = 'n';
        }
        //USARTWriteChar(48+aruco);
      }
    }

    else if (command == 'r') {
      Serial_print("Turning right");          // command to rotate right
      set_direction(command);
    }
    else if (command == 'l') {                // command to rotate left
      Serial_print("Turning left");
      set_direction(command);
    }
    else if (command == 'b') {                // command to go back
      Serial_print("Back");
      set_direction(command);
      _delay_ms(400);
    }
    else if(command == 'o') {                 // command to turn 180 degrees from the left direction
      Serial_print("180 Deg");
      turn_left(1);
    }
    else if(command == 'z') {                  // initially to detetct the ids a special command z is given 
      aruco=0;
      command='s';
      Base_servo();                            // servo is rotated right initially without changing the servo orientation all the blocks and aruco ids are detected
      ++aruco;
      //USARTWriteChar(48+aruco);
    }
    else if(command == 'q') {                  // right side block picking from shrub region
      SERVO.pick_block(0,37);
      command='n';
    }
    else if(command == 'Q') {                  // left side blockpicking from the shrub region
      SERVO.pick_block(0,9);
      command='n';
    }
    else if(command == 'u') {                  //  left side block picking
      SERVO.pick_block(0,14);
      command='n';
    }
    else if(command == 'U') {                  // right side block picking
      SERVO.pick_block(0,37);
      command='n';
    }
    else if(command == 't') {                 // trash picking from left 
      SERVO.pick_block(1,13);
      command='n';
    }
    else if(command == 'T') {                 // trash placing from right
      SERVO.pick_block(1,34);
      command='n';
    }
    else if(command == 'w'){
      SERVO.place_block(1,15);                // placing block to the left 
      command='n';
    }
    else if(command == 'W'){
      SERVO.place_block(1,33);                // placing block to the right
      command='n';
    }
    else if(command == 'p') {                 // placing block in the trash deposition zone
      PORTB &= ~(1 << PB0);
      PORTD |= (1 << PD7);
      PORTB &= ~(1 << PB3);
      PORTB |= (1 << PB4);
      OCR1B = 42125;
      OCR1A = 50000;
      _delay_ms(500);
      OCR1B = 0;
      OCR1A = 0;
      if(trash_count==0) {
        SERVO.place_block(0,21);                //initially to the right 
        trash_count++;
      }
      else {
        SERVO.place_block(0,27);               //then to the left 
        trash_count++;
      }
      command='n';
    }
    else if (command == 'g') {
      SERVO.base.turn(12);                   // to detect the position of the trash in the special case of trash and no service requirement if it is to the right or to the left.
      command = 'n';                        // n means HALT here 
    }
    else if (command == 'n') {
      Serial_print("Stopped");
      command = 'h';                        // h means HALT here
      set_direction('h');
    }
    else if (command == 'h') {
      //do nothing
      //Serial_print("QQ");
    }
  }
  return 0;
}


