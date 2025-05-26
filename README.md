# ECR-POS
## The general scheme
⋅⋅⋅The integration concerns three systems: ECR, MELLON POS and BANK:

![General Scheme](https://github.com/arbdoescode/ECR-POS/blob/main/images/GeneralScheme.PNG "General Scheme")

⋅⋅⋅The usual flow of communication follows 4 steps:
1. The transactions starts from ECR: the operator selects “payment with card” as form
of payment and ECR sends the corresponding request to POS.
2. POS immediately confirms to ECR the reception of the request and ECR enters into
state to wait for the outcome.
3. POS connects to the bank to ask online authorization or approves the transaction
offline or declines it offline or interrupts the transaction.
4. POS replies to ECR with the final outcome: declined or approved. In case of approval,
POS sends complementary information (transaction number, approval code etc)

## Physical Connections
### CONNECTION OVER TCP/IP
⋅⋅⋅The integration concerns three systems: ECR, MELLON POS and BANK:
![Conn Ip](https://github.com/arbdoescode/ECR-POS/blob/main/images/ConnectionTCP-IP.PNG "Connection Ip")

POS acts as “server” in relation to the ECR and as “client” in relation to the bank. The LAN
switch can be external device or embedded in the cashier machine.
Last chapter provides instructions about how to set up the connection for each POS type.

### CONNECTION OVER USB
⋅⋅⋅This connection is not supported in Axium devices. The connection over USB is also
supported, without any change in the protocol. However, that solution is not widely available
in the existing POS applications.
![Conn Usb](https://github.com/arbdoescode/ECR-POS/blob/main/images/ConnectionUSB.PNG "Connection USB")

## Syntax of the Messages
### Message [ECHO]
It is sent by ECR and initiated by the operator to check the connection with the POS (usually
during the installation). Τhe terminal ID and the POS application version use also to be
completed in the echo message:

**ECR REQUEST:**
```
X/<text>
```

**POS RESPONSE:**
```
X/<text>/T<tid>:<app-version>
```
### Message [AMOUNT]
It is sent by ECR when a new sale is to start. When a cash advance transaction is to be
started “H” needs to be used instead of “A”

**ECR REQUEST:**
```
A/S<session number>/F<amount>:<cur-code>:<cur-exp>
 /D<datetime>/R<ecr-number>/H<operator-number>
 /T<receipt number>/G<vat1>:<vat2>:<vat3>:<vat4>/M<custom-data>
```

### Message [CONFIRMED]
It is sent immediately by POS as first answer to initial request for sale (or refund or void)
of ECR, confirming that the request is being processed.

**POS RESPONSE:**
```
A/S<session number>/F<amount>
```

### Message [RESULT]
It is sent by POS as final answer to initial request for sale (or refund or void) of ECR and
carries the outcome of the transaction.
The answer can be received immediately (if the request was approved or declined offline),
within a few seconds (typical case of online authorization) or even in more than minutes in 
case of slow online communication or delayed PIN entry. It is suggested the setting in ECR
of timeout >150 sec.

**Syntax**
```
R/S<session number>/C<rsp-code>{/D<trans-data>{/P<prn-data>}}
```

Example of declined sale

---
| Hex        | Description           |
| ------------- |:-------------:|
|[211122 123929] ECR connection from [10.1.101.132]| |
|ECR->POS: BYTES 81| |
|00 51 .Q| |
|45 43 52 30 31 30 31 41 2F 53 30 30 30 36 37 37 ECR0101A/S000677|[AMOUNT]|
|2F 46 32 35 30 30 3A 39 37 38 3A 32 2F 44 32 30 /F2500:978:2/D20| |
|32 31 31 31 32 32 31 32 33 36 35 32 2F 52 38 2F 211122123652/R8/| |
|48 31 32 31 2F 54 30 30 30 36 37 37 2F 47 3A 30 H121/T000677/G:0| |
|3A 30 3A 30 3A 30 2F 4D 31 32 33 34 35 36 37 38 :0:0:0/M12345678| |
|39 9| |
|POS->ECR: BYTES 22| |
|00 16 4D 45 4C 30 31 30 31 41 2F 53 30 30 30 36 ..MEL0101A/S0006|[CONFIRMED]|
|37 37 2F 46 32 35 30 30 77/F2500| |
|[211122 123929] ECR request| |
|[211122 123932] TXN-L [1][535178xxxxxx6172][2500]| |
|[211122 123932] Connecting [....................]|online|
|[211122 123935] T [271]===>|authorization|
|. . . . . . . . . . . . . . . . . . . . . . . . . .| |
|[211122 123935] <===H [88]| |
|. . . . . . . . . . . . . . . . . . . . . . . . . .| |
|[211122 123939] TXN-L declined (91) rrn=132630115039| |
|POS->ECR: BYTES 20| |
|00 14 4D 45 4C 30 31 30 31 52 2F 53 30 30 30 36 ..MEL0101R/S0006|[RESULT]|
|37 37 2F 43 33 33 77/C33| |
|[211122 123940] ECR connection closed| |