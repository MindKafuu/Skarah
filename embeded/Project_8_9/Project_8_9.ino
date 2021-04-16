//#include <Servo.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>
#include "CRC8.h"

#define gripperSW A3
#define IR_1 A4
#define IR_2 A5
#define slowfreq 65535
#define positiveJ1 1
#define negativeJ1 0

#define positiveJ3 0
#define negativeJ3 1

#define up 1
#define down 0

#define Hismall7 430
#define Hismall9 180
#define Hismall11 55
#define Hismall13 310

#define Hibig1 360 //
#define Hibig3 20 //
#define Hibig5 295

#define OUT 254
#define IN 253

//------------------------------- define -------------------------------//
int per[4] = {0,30,20,25}; 
unsigned int minfreq[4] = {0,60000,35000,62000};

 //------------------------------- Servo -------------------------------//
//Servo myservo;  // create servo object to control a servo
const int pin_servo = 8;
int time_step, clock_step;
int first_degree = 0;
int Onoffgripper = 9;

//-------------------------------- CRC8 --------------------------------//
CRC8 crc8;
uint8_t checksum = 0;

//-------------------------------- Motor ------------------------------//
int step_joint[4]; 
const int dirPin[4] = {0,2,4,6};  // Direction
const int stepPin[4] = {0,3,5,7}; // Step
float degreePerstep[4] = {0,0.075,0.05,0.1125}; // Degree per Step 0.0025
unsigned int dir[4], right = 1, left = 0, on = 1, off = 0;
const int limit_sw[4] = {0,A0,A1,A2};
const int initail_dir[4]= {0,HIGH,HIGH,LOW};
//const int enPin = 4;

// -------------------------------- Timer --------------------------------//
int max_step[4];
int freq[4];
int steptwofive[4];

byte incomingByte[13];

//--------------------------------- Encoder ------------------------------//
/*int encoderPin1 = 2;
int encoderPin2 = 3;

volatile int lastEncoded = 0;
volatile long encoderValue = 0;

long lastencoderValue = 0;

int lastMSB = 0;
int lastLSB = 0;*/
//------------------------------- Serial ---------------------------------//
   // for incoming serial data
char SM_id = 1;         // state for check potocol
int sum_data=0;         // value check sum
int getPackage = 0;
int count = 0;

void drive_motor(float degree_i,int dir_i,int joint_i);
void On_Off_gripper(int state);

void setup() {
   
  Serial.begin(9600);
  crc8.begin();
//  myservo.attach(pin_servo);  // attaches the servo on pin 8 to the servo object
  pinMode(pin_servo,OUTPUT);
  pinMode(Onoffgripper,OUTPUT);

  pinMode(IR_1,INPUT_PULLUP);
  pinMode(IR_2,INPUT_PULLUP);
  pinMode(gripperSW,INPUT);
  
  for(int i=1; i <= 3; i++){
      pinMode(stepPin[i],OUTPUT);
      pinMode(dirPin[i],OUTPUT);
      pinMode(limit_sw[i],INPUT);
  }

  //wdt_enable(WDTO_8S);
  //wdt_reset();
  
  Serial.println("Controller Reset");
  
//------------------------ Setup Encoder ----------------------//
  //pinMode(encoderPin1, INPUT_PULLUP); 
  //pinMode(encoderPin2, INPUT_PULLUP);

  //digitalWrite(encoderPin1, HIGH); //turn pullup resistor on
  //digitalWrite(encoderPin2, HIGH); //turn pullup resistor on

  //call updateEncoder() when any high/low changed seen
  //on interrupt 0 (pin 2), or interrupt 1 (pin 3) 
  //attachInterrupt(0, updateEncoder, CHANGE); 
  //attachInterrupt(1, updateEncoder, CHANGE);
  //attachInterrupt(digitalPinToInterrupt(encoderPin1), updateEncoder, CHANGE);
  //attachInterrupt(digitalPinToInterrupt(encoderPin2), updateEncoder, CHANGE);
  
  noInterrupts();           // disable all interrupts
  //---- Timer1 ----//
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = slowfreq;            // compare match register 
  TCCR1B |= (1 << WGM12);   // CTC mode
  TCCR1B |= (1 << CS11);    // prescaler 
  //TIMSK1 |= (1 << OCIE1A);  // enable timer compare interrupt
  
  //---- Timer3 ----//
  TCCR3A = 0;
  TCCR3B = 0;
  TCNT3  = 0;
  //OCR3A = slowfreq;            // compare match register 
  TCCR3B |= (1 << WGM12);   // CTC mode
  TCCR3B |= (1 << CS12)||(1 << CS10);    // prescaler 
  //TIMSK3 |= (1 << OCIE1A);  // enable timer compare interrupt
  
  //---- Timer4 ----//
  TCCR4A = 0;
  TCCR4B = 0;
  TCNT4  = 0;
  OCR4A = 30000;            // compare match register 
  TCCR4B |= (1 << WGM12);   // CTC mode
  TCCR4B |= (1 << CS12)||(1 << CS10);    // prescaler 
  //TIMSK4 |= (1 << OCIE1A);  // enable timer compare interrupt
  
  //---- Timer5 ----//
  TCCR5A = 0;
  TCCR5B = 0;
  TCNT5  = 0;
  //OCR5A = slowfreq;            // compare match register 
  TCCR5B |= (1 << WGM12);   // CTC mode
  TCCR5B |= (1 << CS12)||(1 << CS10);    // prescaler 
  //TIMSK5 |= (1 << OCIE1A);  // enable timer compare interrupt
  
  interrupts();             // enable all interrupts
  
  //IR_checkUp();
  //IR_checkDown();
  
  set_home_2();
  //IR_checkUp();
  IR_checkDown();
  //drive_motor(390,up,2);
 /* for(int i = 0; i<= 10; i++){
      drive_motor(100,down,2);
      while(step_joint[2] > 0){delay(10);}
      IR_checkUp();
    }
  */
  
  //drive_servo(0);
  //drive_servo(270);
  /*
  pick_path_planing();
  pathIn_column1(5);
  On_Off_gripper(off);
  pathOut_column1(5);
  //*/
  /*
  out_path_planing();
  pathIn_column1(1);
  pick_out();
  pathOut_column1(1);
  sendbox_column1();
  On_Off_gripper(off);
  set_home_2();*/
  
}
        //--------   Joint 1 , 0 คือ ลบ , 1 คือ บวก  ----------// 
        //--------   Joint 2 , 0 คือ ลง  , 1 คือ ขึ้น  ----------// 
        //--------   Joint 3 , 0 คือ ลวก  , 1 คือ ลบ ----------// 
        
void pick_path_planing(){
    drive_motor(20,up,2);
    drive_motor(43,positiveJ1,1);
    drive_motor(82,positiveJ3,3);
    drive_servo(75);
    while(step_joint[1] > 0 || step_joint[3] > 0){delay(10);}
    keep_box();
    On_Off_gripper(on);
    drive_motor(30,up,2);
    while(step_joint[2] > 0){delay(10);}
 }

void out_path_planing(){
    drive_motor(45,positiveJ1,1);
    drive_motor(15,down,2);
    while(step_joint[1] > 0 || step_joint[2] > 0){delay(10);}
  }

void pick_out(){
    keep_box();
    On_Off_gripper(on);
        
    drive_motor(20,up,2);
    while(step_joint[2] > 0){delay(10);}
  }

 void pick_out_dept(){
    On_Off_gripper(on);
    keep_box();
        
    drive_motor(20,up,2);
    while(step_joint[2] > 0){delay(10);}
  }
void pathIn_column1(int numbox){
  int num = 2;
  drive_servo(75);
  drive_motor(172,positiveJ1,1);
  if(incomingByte[9] == IN){
    drive_motor(74,negativeJ3,3);
  }
  drive_servo(141);
  while(step_joint[1] > 0 || step_joint[3] > 0){delay(10);}
  if(incomingByte[9] == OUT){
      drive_motor(2,positiveJ3,3);
      while(step_joint[3] > 0){delay(10);}
    }
    if(numbox == 1){
        drive_motor(Hibig1,up,2);
      }
    else if(numbox == 3){
        drive_motor(Hibig3,up,2);
      }
    else if(numbox == 5){
        drive_motor(Hibig5,down,2);
      }
    drive_motor(50,positiveJ3,3);
    while(step_joint[2] > 0 || step_joint[3] > 0){delay(10);}
    for(int i = 1; i <= 25; i++){
      num += 1.5;
      drive_motor(2,negativeJ1,1);
      drive_motor(3,positiveJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(141+num);
      while(step_joint[3] > 5){delay(10);}
     }
    drive_servo(160);
    delay(500);
  }

void pathIn_column2(int numbox){
  int num = 2;
  drive_servo(75);
  drive_motor(160,positiveJ1,1);
  if(incomingByte[9] == IN){
    drive_motor(74,negativeJ3,3);
  }
  drive_servo(90);
  while(step_joint[1] > 0 || step_joint[3] > 0){delay(10);}
  if(incomingByte[9] == OUT){
      drive_motor(2,positiveJ3,3);
      while(step_joint[3] > 0){delay(10);}
    }
    if(numbox == 2){
        drive_motor(Hibig1,up,2);
      }
    else if(numbox == 4){
        drive_motor(Hibig3,up,2);
      }
    else if(numbox == 6){
        drive_motor(Hibig5,down,2);
      }
    drive_motor(21,positiveJ3,3);
    while(step_joint[2] > 0 || step_joint[3] > 0){delay(10);}
    for(int i = 1; i <= 12; i++){
      num += 2.5;
      drive_motor(3,negativeJ1,1);
      drive_motor(5,positiveJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(90+num);
      while(step_joint[3] > 5){delay(10);}
     }
    drive_servo(118);
    delay(500);
  }

void pathIn_column3(int numbox){
  int num = 2;
  drive_motor(130,positiveJ1,1);
  if(incomingByte[9] == IN){
    drive_motor(74,negativeJ3,3);
  }
  while(step_joint[1] > 0 || step_joint[3] > 0){delay(10);}
  drive_servo(63);
  if(incomingByte[9] == OUT){
      drive_motor(4,negativeJ3,3);
      while(step_joint[3] > 0){delay(10);}
    }
    if(numbox == 7){
        drive_motor(Hismall7,up,2);
      }
    else if(numbox == 9){
        drive_motor(Hismall9,up,2);
      }
    else if(numbox == 11){
        drive_motor(Hismall11,down,2);
      }
    else if(numbox == 13){
        drive_motor(Hismall13,down,2);
    }
    drive_motor(20,positiveJ3,3);
    while(step_joint[2] > 0 || step_joint[3] > 0){delay(10);}
    for(int i = 1; i <= 12; i++){
      num += 2.5;
      drive_motor(2,negativeJ1,1);
      drive_motor(5,positiveJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(63+num);
      while(step_joint[3] > 5){delay(10);}
     }
    drive_servo(91);
    delay(500);
  }

void pathIn_column4(int numbox){
  int num = 2;
  drive_motor(96,positiveJ1,1);
  if(incomingByte[9] == IN){
    drive_motor(74,negativeJ3,3);
  }
  while(step_joint[1] > 0 || step_joint[3] > 0){delay(10);}
  drive_servo(48);
  if(incomingByte[9] == OUT){ // OUT = 254
      drive_motor(2,negativeJ3,3);
      while(step_joint[3] > 0){delay(10);}
    }
    if(numbox == 8){
        drive_motor(Hismall7,up,2);
      }
    else if(numbox == 10){
        drive_motor(Hismall9,up,2);
      }
    else if(numbox == 12){
        drive_motor(Hismall11,down,2);
      }
    else if(numbox == 14){
        drive_motor(Hismall13,down,2);
    }
    drive_motor(40,positiveJ3,3);
    while(step_joint[2] > 0 || step_joint[3] > 0){delay(10);}
    for(int i = 1; i <= 12; i++){
      num += 3;
      drive_motor(2,negativeJ1,1);
      drive_motor(6,positiveJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(48+num);
      while(step_joint[3] > 5){delay(10);}
     }
    drive_servo(90);
    delay(500);
  }

void pathOut_column1(int numbox){
    int num = 2;
    for(int i = 25; i >= 1; i--){
      num += 1;
      drive_motor(2,positiveJ1,1);
      drive_motor(3,negativeJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(160-num);
      while(step_joint[3] > 5){delay(10);}
     }
     delay(100);
     drive_motor(35,negativeJ3,3);
     while(step_joint[3] > 5){delay(10);}
     if(numbox == 1){
        IR_checkDown();
      }
    else if(numbox == 5 || numbox == 3){
        IR_checkUp();
      }
  }

void pathOut_column2(int numbox){
    int num = 2;
    for(int i = 14; i >= 1; i--){
      num += 2.5;
      drive_motor(3,positiveJ1,1);
      drive_motor(5,negativeJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(130-num);
      while(step_joint[3] > 5){delay(10);}
     }
     if(numbox == 2){
        IR_checkDown();
      }
    else if(numbox == 6 || numbox == 4){
        IR_checkUp();
      }
  }
  
void pathOut_column3(int numbox){
    int num = 2;
    for(int i = 12; i >= 1; i--){
      num += 2.5;
      drive_motor(2,positiveJ1,1);
      drive_motor(5,negativeJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(91-num);
      while(step_joint[3] > 5){delay(10);}
     }
     if(numbox == 7 || numbox == 9){
        IR_checkDown();
      }
    else if(numbox == 11 || numbox == 13){
        IR_checkUp();
      }
  }
  
 void pathOut_column4(int numbox){
    int num = 2;
    for(int i = 11; i >= 1; i--){
      num += 2.5;
      drive_motor(2,positiveJ1,1);
      drive_motor(6,negativeJ3,3);
      while(step_joint[1] > 5){delay(10);}
      drive_servo(90-num);
      while(step_joint[3] > 5){delay(10);}
     }
     if(numbox == 8 || numbox == 10){
        IR_checkDown();
      }
    else if(numbox == 12 || numbox == 14){
        IR_checkUp();
      }
  }

 void sendbox_column1(){
    drive_motor(45,positiveJ1,1);
    drive_motor(65,negativeJ3,3);
    drive_servo(160);
    while(step_joint[3] > 5 || step_joint[1] > 5){delay(10);}
    drive_motor(92,positiveJ3,3);
    drive_servo(35);
    while(step_joint[3] > 5)  {delay(10);}
  }

 void sendbox_column2(){
    drive_motor(55,positiveJ1,1);
    drive_motor(35,negativeJ3,3);
    drive_servo(35);
    while(step_joint[3] > 5 || step_joint[1] > 5){delay(10);}
    drive_motor(90,positiveJ3,3);
    while(step_joint[3] > 5)  {delay(10);}
  }
  
 void sendbox_column3(){
    drive_motor(88,positiveJ1,1);
    drive_motor(35,negativeJ3,3);
    drive_servo(35);
    while(step_joint[3] > 5 || step_joint[1] > 5){delay(10);}
    drive_motor(90,positiveJ3,3);
    while(step_joint[3] > 5)  {delay(10);}
  }
  
 void sendbox_column4(){
    drive_motor(125,positiveJ1,1);
    drive_motor(35,negativeJ3,3);
    drive_servo(35);
    while(step_joint[3] > 5 || step_joint[1] > 5){delay(10);}
    drive_motor(75,positiveJ3,3);
    while(step_joint[3] > 5)  {delay(10);}
  }
  
ISR(TIMER1_COMPA_vect)
{
  if(digitalRead(pin_servo) == HIGH){
      digitalWrite(pin_servo,LOW);
       OCR1A = 5000;
    }
  else{
      digitalWrite(pin_servo,HIGH);
      OCR1A = clock_step;
    }
}

ISR(TIMER3_COMPA_vect){
  //wdt_reset();
    if(digitalRead(limit_sw[1]) == HIGH){
      if(step_joint[1] > 0){
        if(dir[1] == right) digitalWrite(dirPin[1], HIGH); // Motor forward
        else digitalWrite(dirPin[1], LOW);      // Motor backward 
        if(digitalRead(stepPin[1]) == HIGH){
              digitalWrite(stepPin[1], LOW);
              step_joint[1]--;
          } else  digitalWrite(stepPin[1], HIGH);
         /* 
        if(step_joint[1] > (max_step[1] - steptwofive[1])){ // 25 Frist step
          freq[1] = freq[1] - ((slowfreq - minfreq[1])/steptwofive[1]);
          OCR3A = freq[1];
        }
        else if(step_joint[1] < steptwofive[1]){
            freq[1] = freq[1] + ((slowfreq - minfreq[1])/steptwofive[1]);
            OCR3A = freq[1];
          }*/
        }
      } else {
        stop_motor(1);
      }
    /*  
    if(digitalRead(4)== HIGH) digitalWrite(4,LOW);
    else  digitalWrite(4,HIGH);*/
}

ISR(TIMER4_COMPA_vect){
  //wdt_reset();
   if(digitalRead(limit_sw[2]) == HIGH){
      if(step_joint[2] > 0){
        if(dir[2] == right) digitalWrite(dirPin[2], HIGH); // Motor forward
        else digitalWrite(dirPin[2], LOW);      // Motor backward 
        if(digitalRead(stepPin[2]) == HIGH){
              digitalWrite(stepPin[2], LOW);
              step_joint[2]--;
          } else  digitalWrite(stepPin[2], HIGH);
          
        /*if(step_joint[2] > (max_step[2] - steptwofive[2])){ // 25 Frist step
          freq[2] = freq[2] - ((slowfreq - minfreq[2])/steptwofive[3]);
          OCR4A = freq[2];
        }
        else if(step_joint[2] < steptwofive[2]){
            freq[2] = freq[2] + ((slowfreq - minfreq[2])/steptwofive[2]);
            OCR4A = freq[2];
          }*/
        }
      } else {stop_motor(2);}
      /*if(digitalRead(5)== HIGH) digitalWrite(5,LOW);
    else  digitalWrite(5,HIGH);*/
 }

ISR(TIMER5_COMPA_vect){
  //wdt_reset();
  /*if(digitalRead(7)== HIGH) digitalWrite(7,LOW);
   else  digitalWrite(7,HIGH);*/
   
   if(digitalRead(limit_sw[3]) == HIGH){
      if(step_joint[3] > 0){
        if(dir[3] == right) digitalWrite(dirPin[3], HIGH); // Motor forward
        else digitalWrite(dirPin[3], LOW);      // Motor backward 
        if(digitalRead(stepPin[3]) == HIGH){
              digitalWrite(stepPin[3], LOW);
              step_joint[3]--;
          } else  digitalWrite(stepPin[3], HIGH);
          
        if(step_joint[3] > (max_step[3] - steptwofive[3])){ // 25 Frist step
          freq[3] = freq[3] - ((slowfreq - minfreq[3])/steptwofive[3]);
          OCR5A = freq[3];
        }
        else if(step_joint[3] < steptwofive[3]){
            freq[3] = freq[3] + ((slowfreq - minfreq[3])/steptwofive[3]);
            OCR5A = freq[3];
          }
        }
      } else {stop_motor(3);}
      
      /*if(digitalRead(6)== HIGH) digitalWrite(6,LOW);
    else  digitalWrite(6,HIGH);*/
 } 

void drive_servo(int degree){
  TIMSK1 |= (1 << OCIE1A);
  if(degree-first_degree > 0){
      for(int i = first_degree; i <= degree; i++){
        //wdt_reset();
        time_step = map(i, 0, 270, 500, 2500); // us
        clock_step = time_step/0.5;
        OCR1A = clock_step;
        delay(20);
        digitalWrite(pin_servo, HIGH);
      }
    }
    else {
      for(int i = first_degree; i >= degree; i--){
        //wdt_reset();
        time_step = map(i, 0, 270, 500, 2500); // us
        clock_step = time_step/0.5;
        OCR1A = clock_step;
        delay(20);
        digitalWrite(pin_servo, HIGH);
      }
    }
   first_degree = degree;
   //stop_motor(4);
}

void updateEncoder(){
  /*int MSB = digitalRead(encoderPin1); //MSB = most significant bit
  int LSB = digitalRead(encoderPin2); //LSB = least significant bit

  int encoded = (MSB << 1) |LSB; //converting the 2 pin value to single number
  int sum  = (lastEncoded << 2) | encoded; //adding it to the previous encoded value

  if(sum == 0b1101 || sum == 0b0100 || sum == 0b0010 || sum == 0b1011) encoderValue ++;
  if(sum == 0b1110 || sum == 0b0111 || sum == 0b0001 || sum == 0b1000) encoderValue --;
 
  lastEncoded = encoded; //store this value for next time*/
}

void stop_motor(int joint_stop){
  if(joint_stop == 1){
      TIMSK3 &= ~(1 << OCIE1A);
      step_joint[1] = 0;
    }  
  else if(joint_stop == 2){
      TIMSK4 &= ~(1 << OCIE1A);
      step_joint[2] = 0;
    } 
  else if(joint_stop == 3){
      TIMSK5 &= ~(1 << OCIE1A);
      step_joint[3] = 0;
    } 
  else if(joint_stop == 4){
      TIMSK1 &= ~(1 << OCIE1A);
    } 
}

void clear_buffer(){
  while((step_joint[1] > 0) || (step_joint[2] > 0) || (step_joint[3] > 0)){
    delay(1000);
    }
  delay(10);
  serialFlush();
  Serial.println( "Done\n");
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
}

void loop() {
  if(Serial.available() >= 13){
      for(int i = 0; i < 13; i++){
          incomingByte[i] = Serial.read();
        }
      if(incomingByte[10] == 255){ 
          set_home();
          drive_motor(380,1,2);
          serialFlush();
          Serial.println( "sethome\n");
      }
      else {
        checksum = crc8.get_crc8(incomingByte, 12);
        if(checksum == incomingByte[12]){ 
          if(incomingByte[9] == IN){
              pick_path_planing();
              if(incomingByte[10] == 1) {
                  pathIn_column1(incomingByte[11]);
                  On_Off_gripper(off);
                  pathOut_column1(incomingByte[11]);
                }
              else if(incomingByte[10] == 2){
                  pathIn_column2(incomingByte[11]);
                  On_Off_gripper(off);
                  pathOut_column2(incomingByte[11]);
                }
              else if(incomingByte[10] == 3){
                  pathIn_column3(incomingByte[11]);
                  On_Off_gripper(off);
                  pathOut_column3(incomingByte[11]);
                }
              else if(incomingByte[10] == 4){
                  pathIn_column4(incomingByte[11]);
                  On_Off_gripper(off);
                  pathOut_column4(incomingByte[11]);
                }
            }
          else if(incomingByte[9] == OUT){
              out_path_planing();
                if(incomingByte[10] == 1){
                    pathIn_column1(incomingByte[11]);
                    if(incomingByte[11] == 5){
                        pick_out_dept();
                      }
                    else pick_out();
                    pathOut_column1(incomingByte[11]);
                    sendbox_column1();
                  }
                else if(incomingByte[10] == 2){
                    pathIn_column2(incomingByte[11]);
                    if(incomingByte[11] == 6){
                        pick_out_dept();
                      }
                    else pick_out();
                    pathOut_column2(incomingByte[11]);
                    sendbox_column2();
                  }
                else if(incomingByte[10] == 3){
                    pathIn_column3(incomingByte[11]);
                    if(incomingByte[11] == 13){
                        pick_out_dept();
                      }
                    else pick_out();
                    pathOut_column3(incomingByte[11]);
                    sendbox_column3();
                  }
                else if(incomingByte[10] == 4){
                    pathIn_column4(incomingByte[11]);
                    if(incomingByte[11] == 14){
                        pick_out_dept();
                      }
                    else pick_out();
                    pathOut_column4(incomingByte[11]);
                    sendbox_column4();
                  }
              On_Off_gripper(off);
            }
            set_home_2();
            serialFlush();
            Serial.println( "correctcheck\n");
        }
         else{
            delay(500);
            serialFlush();
            Serial.println( "nocheck\n");
         }
      }
   }
}
  
void drive_motor(float degree_i,int dir_i,int joint_i){
  step_joint[joint_i] = degree_i / degreePerstep[joint_i];
  max_step[joint_i] = degree_i / degreePerstep[joint_i];
  steptwofive[joint_i] = (max_step[joint_i]*per[joint_i])/100;
  dir[joint_i]= dir_i;
  
  while(digitalRead(limit_sw[joint_i]) == LOW){
    for(int i = 0; i <= (5/degreePerstep[joint_i]); i++){
      digitalWrite(dirPin[joint_i], initail_dir[joint_i]);
      if(digitalRead(stepPin[joint_i]) == HIGH){
        digitalWrite(stepPin[joint_i], LOW);
        step_joint[joint_i]--;
        delay(5);
      } else  digitalWrite(stepPin[joint_i], HIGH); delay(5);
    }
  }
  
  if(joint_i == 1){
      OCR3A = slowfreq;
      freq[1] = slowfreq;
      TIMSK3 |= (1 << OCIE1A);
    }  
  else if(joint_i == 2){
    OCR4A = 23000;
    freq[2] = slowfreq;
    TIMSK4 |= (1 << OCIE1A);
    } 
  else if(joint_i == 3){
    OCR5A = slowfreq;
    freq[3] = slowfreq;
    TIMSK5 |= (1 << OCIE1A);
    } 
}

void On_Off_gripper(int state){
    if(state == on) {digitalWrite(Onoffgripper, HIGH);}
    else {digitalWrite(Onoffgripper, LOW);}
    delay(1000);
}

void IR_checkUp(){
    drive_motor(800,1,2);
    while(digitalRead(IR_1) == HIGH || digitalRead(IR_2) == HIGH){
        delay(10);
      }
    stop_motor(2);
  }

void IR_checkDown(){
    drive_motor(800,0,2);
    while(digitalRead(IR_1) == HIGH || digitalRead(IR_2) == HIGH){
        delay(10);
      }
    stop_motor(2);
  }
  
void set_home(){
      drive_servo(0);
      drive_motor(400,0,1);
      drive_motor(400,1,3);
      while(digitalRead(limit_sw[1]) == HIGH || digitalRead(limit_sw[3]) == HIGH){
          delay(100);
        }
      stop_motor(1);
      stop_motor(3);

      drive_motor(800,0,2);
      while(digitalRead(limit_sw[2]) == HIGH);
      stop_motor(2);
}

void set_home_1(){
      drive_servo(0);
      drive_motor(400,0,1);
      drive_motor(400,1,3);
      drive_motor(1000,0,2);
      while(digitalRead(limit_sw[1]) == HIGH || digitalRead(limit_sw[3]) == HIGH || digitalRead(limit_sw[2]) == HIGH){
          delay(100);
        }
      stop_motor(1);
      stop_motor(3);
      stop_motor(2);
}

void set_home_2(){
      drive_servo(10);
      drive_motor(400,0,1);
      drive_motor(400,1,3);
      while(digitalRead(limit_sw[1]) == HIGH || digitalRead(limit_sw[3]) == HIGH){
          delay(100);
        }
      stop_motor(1);
      stop_motor(3);
}

void keep_box(){
    while(digitalRead(A3) == HIGH){
        drive_motor(12,0,2);
        delay(100);
      }
    stop_motor(2);
    delay(300);
    //drive_motor(count,1,2);
    //delay(1000);
  }
