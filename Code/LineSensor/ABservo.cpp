/*
 ? Team Id: 288
 ? Author List: Aditya Kumar Singh, Karthik S.
 ? Filename: ABservo.cpp
 ? Theme: AntBOT
 ? Functions: timer02(), Grip::turn(), Grip::_grip(), grip::_release(),Arm::bend(),Arm::lift(),Arm::bend(),Base::turn,Base::center(),Base::left(),Base::right(),Servo_::Servo_(),Servo_::place_block(),Servo_::pick_block()
 ? Global Variable: None
 */




#include "ABservo.h"
#include<avr/io.h>
#include<util/delay.h>
#include<avr/interrupt.h>

ISR(TIMER2_OVF_vect) {
  PORTD|=(1<<4);
}
ISR(TIMER2_COMPA_vect) {
  PORTD&=~(1<<4);
}

/*
 ? Function Name: timer02()
 ? Input: None
 ? Output: None
 ? Logic: Iniatiallise timer 0,1,2 and servos in the initial position
 ? Example timer02()
 */

void timer02() {
  sei();
  DDRD |= (1 << 5) | (1 << 6) | (1 << 3) |(1<<4);
  //Initila duty cycle 0
  OCR0A = 16;                                          //gripper initially released
  OCR0B = 8;                                           //arm initially postion
  TCCR0A |= (1 << COM0A1) | (1 << COM0B1);             //Non-inverting mode
  //Fast PWM
  TCCR0A |= (1 << WGM00) | (1 << WGM01);
  TCCR0B |= (1 << CS02) | (1 << CS00);                              //Start the Timer with 1024 prescaler
  
  OCR2A = 30;
  OCR2B = 10;                          // base initially facing the center
  TCCR2A |= (1 << COM2B1);             //Non-inverting mode
  //Fast PWM
  TCCR2A |= (1 << WGM20) | (1 << WGM21);
  TCCR2B |= (1 << CS22) | (1 << CS21) | (1 << CS20);     // 1024 prescaler for timer 2
  TIMSK2=0b00000011;
}


/*
 ? Function Name: Grip::turn()
 ? Input: duty
 ? Output: None
 ? Logic: turns the gripper to the specified angle
 ? Example : Grip::turn(16)
 */
void Grip::turn(int duty) {
  OCR0A = duty;
}
/*
 ? Function Name: Grip::_grip()
 ? Input: None
 ? Output: None
 ? Logic: grips the block when bought near the block
 ? Example : Grip::_grip()
 */


void Grip::_grip() {
  OCR0A = grip_;
  OCR2A= 9;
}

/*
 ? Function Name: Grip::_release()
 ? Input: None
 ? Output: None
 ? Logic: releases the block
 ? Example : Grip::_release()
 */


void Grip::_release() {
  OCR0A = release_;
  OCR2A= 30;
}

/*
 ? Function Name: Arm::turn()
 ? Input: duty
 ? Output: None
 ? Logic: turns the arm to the specified angle
 ? Example : Arm::turn(8)
 */

void Arm::turn(int duty) {
  OCR0B = duty;
}


/*
 ? Function Name: Arm::bend()
 ? Input: none
 ? Output: None
 ? Logic: bend position of arm
 ? Example : Arm::bend()
 */

void Arm::bend() {
  OCR0B = bend_;
}


/*
 ? Function Name: Arm::lift()
 ? Input: none
 ? Output: None
 ? Logic: lifts the arm  
 ? Example : Arm::lifts()
 */

void Arm::lift() {
  OCR0B = lift_;
}

/*
 ? Function Name: Base::turn()
 ? Input: duty
 ? Output: None
 ? Logic: turn the base according to the input duty cycle
 ? Example : Base:turn(35)
 */

void Base::turn(int duty) {
  OCR2B = duty;
}

/*
 ? Function Name: Base::center()
 ? Input: none
 ? Output: None
 ? Logic: brings base to the center
 ? Example : Base::center()
 */

void Base::center() {
  OCR2B = center_;
}

/*
 ? Function Name: Base::left()
 ? Input: none
 ? Output: None
 ? Logic: turns the base to left  
 ? Example : Base::left()
 */

void Base::left() {
  OCR2B = left_;
}

/*
 ? Function Name: Base::right()
 ? Input: none
 ? Output: None
 ? Logic: turns the base to right
 ? Example : Base::right()
 */

void Base::right() {
  OCR2B = right_;
}

/*
 ? Function Name: Servo_::Servo_()
 ? Input: none
 ? Output: None
 ? Logic: initiallise allthe servos to the initiall position and align the base to the center
 ? Example : Servo_::Servo_()
 */

Servo_::Servo_() {
  timer02();
  base.center();

}
/*
 ? Function Name: Servo_::pick_block()
 ? Input: back and base_angle 
 ? Output: None
 ? Logic:  It comes back in anthill region for picking , but in the shrub area it doesnt come back and performs the necessary operations to pick up block
 ? Example : Servo_::pick_block(1,35)
 */

void Servo_::pick_block(int back, int base_angle) {
  if (back) {                                         //if back is one it comes a little back and stops there
    PORTB &= ~(1 << PB0);
    PORTD |= (1 << PD7);
    PORTB &= ~(1 << PB3);
    PORTB |= (1 << PB4);
    OCR1B = 42125;
    OCR1A = 40000;
    _delay_ms(400);
    OCR1B = 0;
    OCR1A = 0;
  }
  grip._release();                                    //logic to pick_block 
  base.turn(base_angle);
  _delay_ms(1000);
  arm.bend();
  _delay_ms(1000);
  grip._grip();
  _delay_ms(1000);
  arm.lift();
  _delay_ms(1000);
  base.center();
  _delay_ms(1000);
}

/*
 ? Function Name: Servo_place::place_block()
 ? Input: back and base angle
 ? Output: None
 ? Logic: it comes back for a small time to place block in anthill region by performing the necessary operations to place block
 ? Example : Servo_place::place_block(1,14)
 */

void Servo_::place_block(int back, int base_angle) {
  if (back) {
    PORTB &= ~(1 << PB0);             //if back is one it comes a little back and stops there
    PORTD |= (1 << PD7);
    PORTB &= ~(1 << PB3);
    PORTB |= (1 << PB4);
    OCR1B = 42125;
    OCR1A = 40000;
    _delay_ms(500);
    OCR1B = 0;
    OCR1A = 0;
  }
  base.turn(base_angle);
  _delay_ms(1000);                     //logic to place_block 
  arm.bend();
  _delay_ms(1000);
  grip._release();
  _delay_ms(1000);
  arm.lift();
  _delay_ms(1000);
  base.center();
  _delay_ms(1000);
}
