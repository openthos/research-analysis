Alice, a service provider like Paypal or Steam, consider to move his service to cloud. 放在云的好处包括容易配置，不需维护。He may still concern about his data's security. Data access pattern is one sensitive information should be hide, several system [sundr, privatefs,oblivistore, taostore] made effort on this problem with oblivious RAM based protocols. The cloud server still need to protect the data's secure, ie. confidentiality, integrity and freshness. Data's confidentiality and integrity can be protected by encryption and signature. But for the freshness, additional approach requested.

Let's see an example about why freshness is important:
Assume inside the datacenter, a mailcious operator Bob can monitor all traffic of system and modify disk as he want. Since Bob don't want to be arrested, all the activity should be silent. He can only do manipulation which inference the availablity or performance on small number of machine in the datacenter. Every mailcious opeartion will be camouflage as a normal system failure. Alice's service is public, so everyone can register on it. Bob register as a user of Alice's service, charge $100. Bob find the data location corresponding to his account by the traffic analysis and remember the content of encrypted $100. It's ok even though he might not able to locate presicely under the oblivious RAM protocol. After that, Bob spend some money like $99 and then restore the content of $100 back to the disk. As a result, after Bob spend $99, he still have $100 now.
Such scenario may happens inside one company as [sundr,oblivistore] assumed since the a large company can't promise every employee is honourable. Inside the company, one employee can access machine as well as the client account.

To protect freshness across power cycle, one naive way is track the version(nonce) of every file in secure non-volatile storage.  However, secure hardware only provide a small size trust non-volatile memory. [Shroud] is a work keep data secure based on oblivious RAM with falut-tolerence. [Shroud] keep a merkle tree of files and bind the root of merkle tree with a counter inside non-volatile memory. Since [Shroud] do not handle user request concurrently, increase an global counter in the system is not complicated. But the maintenance of merkle tree introduce nearly 300% overhead for small size objects.
Even regardless of the freshness protection, oblivious RAM is not suit for storage: there is no dependency between file objects, but ORAM introduce lots of conflict inter request and extra read and write in one request.

Fortunately, Intel SGX, a new hardware based trusted execution environment, which can supply large secure volatile memory, encounter same problem about rollback attack protection.

[ROTE], one system for rollback protection with Intel SGX, use the similar technology as shroud did. Each machine maintain one Merkle tree inside secure but volatile memory. Everytime updating a file invoke updating the Merkle tree, store Merkle tree to non-volatile but untrusted disk and broadcast the root of merkle tree to other trusted platform. Once the system crash and the Merkle tree inside volatile memory lost, the machine will retrieve the root of Merkle tree from other platform and validate the Merkle tree store on disk.

In such system, crash 是主要问题。


On the other hand, as a cloud storage system, horizontal scaliability is also critical. Different service provider may want to host their service on cloud.


We present Yard,
DHT
