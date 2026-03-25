class BudApp:
    def __init__(self, iniBud , balance , transaction , spent):
        self.iniBud = iniBud
        self.balance = balance
        self.transaction = transaction
        self.spent = spent

    def Init_Bal(self):
        print(f'\nYour initial budget was ${abs(self.iniBud):,.2f}.')

    def Balance_left(self):
        if self.balance >= 0:
            print(f'\nYou have ${abs(self.balance):,.2f} left in your budget.')

        else:
            print(f'\nYou are ${abs(self.balance):,.2f} overbudget.')

# New Transaction - Allows user to enter the category they spent money on,
#                   a description of what they spent on, & how much it cost.
#
# Updates the total balance and spent variables in bud_class                  

    def Transaction(self):
        valid_input = False
        while not valid_input:
            try:
                print("\nEnter the cost of the item: ", end='$')
                usr_tra = float(input())

                if usr_tra <= 0:
                    print("Invalid value. Please try again.\n")
                elif usr_tra > 0:
                    valid_input = True
                    self.transaction = usr_tra
            except(ValueError):
                print("The value you entered is invalid. Please try again.\n")
        self.balance -= self.transaction
        self.spent += self.transaction
        
        ''' #Unfinished Category
    print('\n      What category you spent on')
    print('-'*38)
    print(f'Utilities (U)  Credit (C)   Travel (T)')
    print(f'Medical (M)  Shopping (S)      Fun (F)')
    print(f'                Other (O)')
    print('Enter a category: ', end='')
    valid_input = False
    while not valid_input:
        usr_choice = input()

        if usr_choice in ['C','T','M','S','F','O',
                          'c','t','m','s','f','o']:
            valid_input = True
            return str(usr_choice)
        else:
            print('Incorrect Choice.  Enter again:', end=' ')
        '''

# Amount Spent - Shows how much the user has spent in total    

    def Spent(self):
        print(f'\nYou spent ${self.spent:,.2f} in total')
