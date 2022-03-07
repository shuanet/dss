#!/usr/bin/python3
"""
USSP Main.
"""

import USSP


def main():
    """
    Create USSP1 and USSP2, USSP1 ows an ISA, and USSP2 subscribes to it.
    """
    print("Starting USSPs\n")
    ussp1 = USSP.USSP('ussp1', 8094)
    ussp2 = USSP.USSP('ussp2', 8091)
    ussp1.authentify_read()
    ussp1.authentify_write()
    ussp2.authentify_read()
    ussp2.authentify_write()
    isa_id_1 = ussp1.create_isa()
    isa_json = ussp2.get_isa(_isa_id=isa_id_1)
    ussp2.subscribe()

    print("\nDeleting ISAs\n")
    ussp1.delete_isa(isa_json["id"], isa_json["version"])
    ussp2.delete_subscription()
    

if __name__ == "__main__":
    main()
