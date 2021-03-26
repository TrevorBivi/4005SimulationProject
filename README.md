# SYSC 4005 Project Files

## Files

### simulator.py
Our main simulation implementation

### simulator_iter.py
Our originial simulation implementation. Splits time into finite chunks. This is a more straightforward and foolproof implemenation but much slower. However, making it benefited use greatly as it can be used to help verify the results of our model.

### /inputModeling
Contains expoModeling.py which was used to aid in imput modeling for milestone 2

### /sensitivity analysis
Contains python files used for model verification for milestone 3. These files can be used to generate graphs that show how modifying model input affects output. The versions ending with _iter test with the originial simulation implementation. The ones ending with _noiter test the new implementation. Both should give very similar results.
