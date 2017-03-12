Reading notes for Haven
Haven is the first system using SGX, so it's the entry for me to understand the mechanism about sgx.
## Motivation
Protect Application from cloud by using hardware on x86.

## Goal:
Confidentiality:
The execution of the shielded program appears as a black box to the rest of the system. Only its input and output are observable.
Integrity:
The system cannot affect the behavior o the program, except by choosing not to execute it at all or withholding resources.

## Background/SGX
SGX is the intel Secure Guard eXtension.
### Memory protection
The secure zone is called enclave. Then enclave data is protected by CPU access control(The TLB).
SGX mediates page mappings at enclave setup and maintains shadow state for each page. The OS allocate the page for enclave from Enclave page cache(EPC). On each page access, the processor will check page table, enclave mode, the page blongs to EPC and is *correctly typed*.    
Due to the limition of EPC, the processor will flush the content to an encrypted buffer in main memory like swap for normal memory.  

### Attestation  
#### What's attestation
Attestation is a mechanism for software to prove its identity.
#### SGX
SGX support CPU-based attestation.

### Enclave entry and exit
SGX mediate transitions into and out of the enclaves and protects the enclave's register file from OS exception handlers by thread control structure(TCS).

### Dynamic memory allocation
Using EADD to add a page and before EACCEPT execute, the page still remain unaccessible.
