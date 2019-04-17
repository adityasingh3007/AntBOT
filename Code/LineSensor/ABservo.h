#ifndef ABservo_h
#define ABservo_h


/*

class : Base
Positions:Center_,left_ and right_ 
functions:turn(),center(),left(),right()

*/

class Base {
    public:
        int center_ = 24;
        int left_ = 10;
        int right_ = 39;
        //base();
        void turn(int);
        void center();
        void left();
        void right();
};

/*

class : Arm
Positions:bend_ and lift_
functions:turn(),bend(),lift()

*/

class Arm {
    public:
        int bend_ = 22;
        int lift_ = 8;

        //arm();
        void turn(int);
        void bend();
        void lift();
        
};

/*

class : Grip
Positions: grip_ and release_
Funtions: turn(),_grip(),_relese();

*/

class Grip {
    public:
        int grip_ = 28; 
        int release_ = 9;
        //grip();
        void turn(int);
        void _grip();
        void _release();
};

/*

class : Servo_
functions : pick_block and place_block()

*/

class Servo_ {
    public:
        Servo_();
        Base base;
        Arm arm;
        Grip grip;
        void pick_block(int,int);
        void place_block(int,int);
};

void timer02();              // initiallizing the timer02 

#endif
