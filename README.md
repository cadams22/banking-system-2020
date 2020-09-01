# banking-system-2020
##Project Overview
###ATM Design Problem
This project should take approximately four hours to complete.
Write a program that allows a user to deposit or get money from an ATM. Once the program is started, it should accept input until the END
command is sent.
###You should:
Store the amount of money that is in the machine. The machine initially contains $10,000.
Validate any request via an account ID and PIN.
Store individual account data, including transaction history. Attached is a CSV file containing the initial account data. Assume there is no
preexisting transaction history.
Handle any bogus requests with relevant error handling and logging.
Receive and dispense money.
Write unit tests.

##Specification
###Authorize
####Description
Authorizes an account locally until they are logged out. If there is no activity for 2 minutes, your program should automatically log out the account.
####Syntax
authorize <account_id> <pin>
####A successful authorization returns:
<account_id> successfully authorized.
####An unsuccessful authorization returns:
Authorization failed.
####Additional Requirements
Attempts to access any other commands, with the exception of logout and end, without an active authorization should result in:
Authorization required.

###Withdraw
####Description
Removes value from the authorized account. The machine only contains $20 bills, so the withdrawal amount must be a multiple of 20.
####Syntax
withdraw <value>
####If account has not been overdrawn, returns balance after withdrawal in the format:
Amount dispensed: $<x>
Current balance: <balance>
####If the account has been overdrawn with this transaction, removes a further $5 from their account, and returns:
Amount dispensed: $<x>
You have been charged an overdraft fee of $5. Current balance: <balance>
####Additional Requirements
The machine can’t dispense more money than it contains. If in the above two scenarios the machine contains less money than was
requested, the withdrawal amount should be adjusted to be the amount in the machine and this should be prepended to the return value:
Unable to dispense full amount requested at this time.
If instead there is no money in the machine, the return value should be this and only this:
Unable to process your withdrawal at this time.
If the account is already overdrawn, do not perform any checks against the available money in the machine, do not process the withdrawal,
and return only this:
Your account is overdrawn! You may not make withdrawals at this time.

###Deposit
####Description
Adds value to the authorized account. The deposited amount does not need to be a multiple of 20.
####Syntax
deposit <value>
####Returns the account’s balance after deposit is made in the format:
Current balance: <balance>

###Balance
####Description
Returns the account’s current balance.
####Syntax
balance
####Returns the account’s balance in the format:
Current balance: <balance>

###History
####Description
Returns the account’s transaction history.
####Syntax
history
####If there is no history, returns:
No history found
####Otherwise, returns the transaction history in reverse chronological order (most recent transaction first) in the format:
<date> <time> <amount> <balance after transaction>
For example:
2020-02-04 13:04:22 -20.00 140.67
2020-02-04 13:04:01 60.44 160.67
2020-02-04 13:03:49 35.00 100.23

###Log Out
####Description
Deactivates the currently authorized account.
####Syntax
logout
####If an account is currently authorized, returns:
Account <account_id> logged out.
####Otherwise, returns:
No account is currently authorized.

###End
####Description
Shuts down the server.
####Syntax
end
####Behavior
Returns nothing, and ends the program.