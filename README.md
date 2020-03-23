# Re-implementation of quantum-secure algorithm FrodoKEM in Python 3.x

This is Python implementation of FrodoKEM (Key Exchange Mechanism), as a result of my bachelor, based on [Microsoft's implementation in C](https://github.com/Microsoft/PQCrypto-LWEKE/), but using OOP (and NumPy for matrix operations). FrodoKEM is a key exchange protocol, which security is based on Learning With Errors problem - simply put it is a problem of solving a system of linear equations with probabilistic soluton, and is based on mathematical objects with regular structure called lattices. Additionally, I created a demonstration application as well in a form of "terminal-based chat" (using ncurses implementation in Python) as well as simple benchmark tool allowing the programmer to test efficiency of this implementation. FrodoKEM was implemented as a separate module, which is imported and used in Application module. In a short, Python implementation is several hundreds times slower than C, however it provides some educational value and hopefully better understanding of how this algorithm work. I did my best to at least save Microsoft's comments on what is going on in particular places of the code, as well as put mine in places which I was sure I did understand. Finally, my implementation is much shorter and gives a simple to use, abstract interface for the programmer to use it. It is also most likely as secure as Microsoft's implementation is. 


General structure
------
Similarly to Microsoft's implementation, the structure of source files is maintained. Going top-down, there is *test_kem.py* that server an interface to interact, test, benchmark FrodoKEM. Next up, there is *FrodoAPI640* file/class, which implements parameters for the lowest-security-level version of FrodoKEM (accoring to NIST proposals) - targeting bruteforce security of **AES-128**. The other versions of FrodoKEM, namely FrodoKEM-976 and FrodoKEM-1344, targeting respectively AES-192 and AES-256 are not implemented, but all the underlying methods were in fact coded, so implementing these variations is simply a matter of creating new class, adding parameters and connecting correct methods. Going down, next class to discuss is CryptoKEM. This is where all high-level mechanisms of FrodoKEM reside - *key generation*, *key encapsulation* and *key decapsulation*. It is worth to note here that FrodoKEM uses key exchange protocol based on LWEKE scheme (Learning With Errors Key Exchange), which is a bit different from Diffie-Hellman scheme. The difference is, LWEKE is not as symmetric as D-H, because both *key generation* and *key encapsulation* are probabilistic algorithms. The bottom level of files/classes structure belongs to *Frodo*, where all the abstract mathematical functions for FrodoKEM were implemented. *SHA202* implements **SHAKE** functions and **KECCAKf1600** permutations used to generate the matrix A. The *noise.py* and *util.py* files are complementary functions that have implemented some basic operations which FrodoKEM uses. General UML-like diagram shows the discussed dependencies: 


![FrodoKEM Structure](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/frodo_kem_structure.png)

Another side of the store is demonstration application (Application module). It has two basic capabilities - you can use it either as a benchmark tool for FrodoKEM implementation in Python, or use its demonstration part which is basic terminal-based internet chat. Communication is done over TCP sockets as a basic client-server scenario. In fact, when you set up server, you can connect as many clients as the server has allowed connections, and it is basically a chatroom (i.e. all connected clients see each other messages. The chat has two versions - visual (implemented using ncurses library) and text. Structure of this module is divided into two main classes: *ChatManager* and *ConnectionManager*. The former is responsible for getting input from the user, processing it, sending to *ConnectionManager*. The latter implements all connection mechanisms in a form of RPC (Remote Procedure Call) server (*RemoteAPI* subclass), which shares an API to exchange keys (using *KeyExchanger* class), send messages or files to all the clients, who in turn use this API to communicate with the server. In order to provide security, the *Encryption* subclass uses encryption mechanisms to encrypt messages using AES-128 in ECB mode (I know, not the most secure solution, but it's just for demonstration purposes). Both *KeyExchanger* and *Encryption* classes are implemented in such a way so changing the default cryptosystem on any of them is possible. Perhaps it will be a little more difficult to connect another key exchange mechanism because not many of them use LWEKE scheme. The class structure is presented on diagram below:


![Application Structure](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/classess_application.png)


Differences between C and Python implementations
------
This Python implementation of FrodoKEM algorithm  is not only a translation of low-level C functions into standardized, well defined, high-level functions that make the code more concise and understandable, but also extending existing paradigm into Object Oriented Programming (OOP) – thus giving the user convenience of interacting with ready objects that hide beneath all the necessary computations. On the other side, main disadvantage of Python implementation is that it is times slower than its C equivalent – for the price of gained convenience.

*FrodoAPI640* contains algorithm parameters, such as length of keys and other relevant vectors enclosed in a subclass called Params. This class is later passed into all three functions, so that *CryptoKEM* can use these parameters. On object creation of *FrodoAPI640* all the important vectors are created and zeroed – keys and encapsulated keys. Initialization is also repeated each time *crypto_kem_keypair_frodo640()* function is called – so that before each key generation all vectors are cleared up.
Considering structure of the code itself, most important difference is a higher level of abstraction in Python implementation. Data types, pointers and loops are now handled by Python, which covers successfully all details, giving programmer a clean interface with list objects and methods to operate on them. Moreover, Python is straightforwardly extendable with an extensive number of open-source libraries. Thus, most of the time programming a solution in Python is a matter of finding a proper library that has it already implemented. In case of scientific operations on matrices one of most popular choices is *NumPy library*. It also provides C-compatible data types for its arrays, which helped in keeping implementation closer to the original. Other libraries used generally in this project include *PyCryptodome* which provided AES implementation and Secrets, that was used for generating cryptographically secure random tokens, according to its documentation. One advantage of using Python is simplicity of importing any libraries and using them in own project. It is possible to import only necessary functions from any library, and all dependencies are handled by Python interpreter. This way, much of the code is decentralized from the project and accessed whenever needed instead of being stored in a complicated structure of source files. Those imported functions later replace most of the loops from original implementation, which is shown on the figure below to show main difference between Pythonic way to handle matrix computations on one hand, and the same code written in C. 

![Microsoft's implementation](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/comparison_c.png)

And the same snipped of code in Python:

![Python implementation](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/comparison_py.png)

Python implementation of the same function hides all the logic under functions that operate on entire vectors, not just their single elements. It is possible to re-write the code from C to Python with all these loops instead of functions, but it is certainly not a Pythonic way for this task, and it would result in a much slower execution comparing to the same code that uses functions, not loops. All the loops are of course inside these functions and it is surely better to let Python take care of them. Python version might seem a little overwhelming at first, with all these nested functions and ranges but it is only before one takes a closer look at official documentation of these functions, which clearly explains what arguments they take and what output is expected. This means that a programmer does no longer care about how i.e. matrix multiplication is computed – but only what to put inside it. Also, one may notice that since it is just matrix multiplication and addition, it should be much shorter in Python, calling only i.e. multiply() and sum() functions. However, as this is not standard matrix multiplication but a slightly modified version, it could not be therefore simplified more. This is usually the case in many other functions of Microsoft’s FrodoKEM implementation. 

Examples
------
This section provides information about basic usage of *Application* module. In order to get help, run module without any arguments: 

** # python3 -m Application **

You will be presented with the following information: 

![Commandline options](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/command_line_options_application.png)

The purpose of Chat feature in Application module is the presentation of Python’s FrodoKEM implementation in real-world scenario. The tool has a --secure option which starts secure connection with the server to exchange messages or ensures that server accepts only secure connections (when used with the server). Chat in the visual mode is presented on the figure below, and is run with the following command: 

** # python3 -m Application -l --mode visual ** 


![Visual](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/application_visual.png)

Application looks similarly in client mode. In order to run it, use *-c* options instead of *-L*. In order to start Chat in text mode, change *visual* parameter to *text* (which is also the default mode). The screen looks as follows in server mode: 

** # python3 -m Application -l --mode text ** 

![Text - server](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/application_text_server.png)

As can be seen on the figure, it automatically outputs all the debugging information to the stdout. In visual mode, all the logs are pushed to files marked with the current date. And this is how looks client in text mode: 

** # python3 -m Application -c --mode text ** 

![Text - client](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/application_text_client.png)

To wrap up, logic of this application is as follows - server is started at a specific port and address, either in the visual or text mode. In visual mode, only messages sent to the server are displayed in the window, and all logs are sent to the log file residing in the same directory as server. The same is for client – either visual or text mode, in the former logs go to the log file, in the latter – they are printed on the std output. Server accepts specific number of connections, which can be set with an option. It has a function of “chat room” – clients connect to it, send messages, and every message server received is sent to all connected clients, except the sender. After connecting to the server, client starts a separate thread on a specific port that listens for any incoming messages from the server. This behavior is similar to push & poll mechanism from observer pattern (Okhravi, n.d.)  

Benchmarking
------



Fail rate of Python implementation
------
There is one caveat that comes with this implementation in Python. Once for a time the encapsulation-computed shared secret vector does not equal the one generated by decapsulation. This issue was thoroughly tested and compared with results of Microsoft’s implementation. The only source of uncertainty in the key generation is one randomly generated vector at the beginning of the algorithm, and there is similar generation as well in encapsulation algorithm. Decapsulation algorithm is completely deterministic. The problem is, for some of these mentioned randomized vectors the issue persists (only in Python implementation). It was not possible to find the source of the issue.  In order to picture this with concrete numbers, the following tests were run with command:

** # python3 -m Application  --test  --fails  --number 1000 **

![Microsoft's implementation](https://github.com/PrzemyslawSamsel/AgainstQuantum/blob/master/images/fail_rate_python.png)

The Application module was run with specific options in order to deliver results of tests run 1000 times – key generation, encapsulation, decapsulation and comparison of computed shared secret vectors. There were only 2 incorrect results (mismatch) and 998 correct – failure rate is extremely small. The Python script shows current operation, current iteration (with a progress bar below) and based on n-1 iteration (starting iteration nr. n=1) it approximates estimated run time. The tests run 19528.35 seconds ( ~ 330 mins => 5,5 hrs).

