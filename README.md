This is a Pygame that allows you to build your own sequential or combinatorial circuit:
User Guide:
  1)  *Left click* on toolbar to spawn logic gate blocks
  2)  *Left click and drag* block to move it
  3)  *Left click and drag* wire from output ports to input ports to connect blocks
  4)  *Left click* on input block to enter typing mode
      * input 0 or 1
      * *backspace* to delete last input
      * *enter* to exit typing mode
  5)  *Right click* on wires or blocks to delete
  6)  *Space* to advance a clock cycle
      * least significant bit goes throught the circuit first
      * least significant bit gets outputed first
      * when input is exhausted, it is defaulted to 0 
      
