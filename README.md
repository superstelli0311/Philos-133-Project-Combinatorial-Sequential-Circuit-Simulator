This is a Pygame that allows you to build your own sequential or combinatorial circuit:  

Installation Guide:
  1) download and unzip **CircuitSimulator.zip**
  2) run exe file
      * if warning of malware appears, go to **System Settings** -> **Privacy and Security** -> **Security** -> and select **Allow Anyway**

User Guide:
  1)  *left click* on toolbar to spawn logic gate blocks
  2)  *left click and drag* block to move it
  3)  *left click and drag* wire from output ports to input ports to connect blocks
  4)  *left click* on input block to enter typing mode
      * input 0 or 1
      * *backspace* to delete last input
      * *enter* to exit typing mode
  5)  *right click* on wires or blocks to delete
  6)  *space* to advance a clock cycle
      * least significant bit goes throught the circuit first
      * least significant bit gets outputed first
      * when input is exhausted, it is defaulted to 0 
      
