i# CUSTOM USS


Before creating our USSPs, we need to have the DSS running:
```
$ cd dss/build/dev
$ ./run_locally.sh
```

Run run_uss_instance.md
```
$ ./run_uss_instance.md
```

Then you can create an USSP. 
```
create_ussp ussp_id localhost_port
```
You must specify an ussp_id and a port for localhost (between 1000 and 9999).
For example: 
```
create_ussp my_custom_ussp 9090
```
You can open as many terminals as you want and create as many ussps as you want. 

---
Once you have your USSPs running, you can type the following commands to manage ISAs and subscriptions for each USSP.

ISA management:
* You can create a custom ISA: 
`create_isa name geometry time_start time_end` 
* For testing purposes, you can create a predefined ISA, encompassing Toulouse and its surroundings, named TOULOUSE, starting now and lasting for a day: 
`create_isa toulouse`
* Once the ISA is created, it is only known by the USSP that created it. Once you are happy with the ISA, you can submit it to the DSS, passing either an ID or name as argument:
`submit_isa isa_id/isa_name`
* You can also delete the ISA both from the USSP memory and the DSS, passing either an ID or name as argument:
`delete_isa isa_id/isa_name`

Subscription management (same as for the ISAs):
* Create subscription:
`create_sub name geometry time_start time_end`
* Create subscription in Toulouse lasting a day:
`create_sub toulouse`
* Submit subscription:
`submit_sub sub_id/sub_name`
* Delete subscription:
`delete_sub sub_id/sub_name`



# SIMU

Run the simu.py file, it extracts the data from DepartureV{1,2,3}.csv generated from RandomDemand.xlsx
It creates an instance of Aircraft class for each aircraft/flight in RandomDemand.

To adjust the speed of the simulation, change the `TIMESTEP` parameter. A high value will make the simulation slower, and a low value will make it quicker (I suggest 0.001 if you want to run it in less than 5 min, 0.01 will take around 50 mins and 1 will take around 12 hours).

What does an instance of Aircraft do?
(NB, all variables in CAPSLOCK are parameters that you are free to modify at the beginning of the simu.py file)
It creates a simulation agent that does the following:
* Waits for `self.start_time - FP_SEND_WINDOW_START`, which represents the time it can start sending its flight plan to the ussp.
* Computes a random number between `FP_SENd_WINDOW_START` and `FP_SEND_WINDOW_END`, waits for this amount of time and sends its flight plan to one of the USSPs in `USSP_LIST` (typically one or two depending on the needs of the simulation).
* Receives the `ussp_start_time` representing the time assigned by the ussp for the flight to start. /!\ This is an indicator of "how well" the VIMS performs, we want to reduce `delay = self.ussp_start_time - self.start_time` as much as we can (this is your job now ;) ).
* Waits for `self.ussp_start_time` to start its flight. Sends an http request to ussp_id/flights/flight_id/start_flight to notice or ask for permission to start flight. Upon acceptance (`status_code == 200`), it starts its flight.
* It waits for `V1_V2_TIME` or `V1_V3_TIME`. This represents the time it needs to fly from its departure vertiport to its arrival vertiport.
* When the time mentionned above has elapsed, it send an http request to the ussp 
ussp_id/flights/flight_id/end_flight to notify it of the completion of the flight.

Finally, when the simulation end or when the user interrupts the simulation (CTRL+C), the code computes the mean_delay of all aircrafts (that had their flight plan accepted by ussp). 

NB: For now we forget about paparazzi, but in the code you may see passages intended for paparazzi, executed `if run_with_pprz`. Don't mind them it's for me to see if we can manage to do it with paparazzi at a later stage. 




