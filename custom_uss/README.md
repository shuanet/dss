# CUSTOM USS


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
$ create_ussp ussp_id localhost_port
```
You must specify an ussp_id and a port for localhost (between 1000 and 9999).
For example: 
```
$ create_ussp my_custom_ussp 9090
```
You can open as many terminals as you want and create as many ussps as you want. 

---
Once you have your USSPs running, you can type the following commands to manage ISAs and subscriptions for each USSP.

Isa management:
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