from datetime import datetime

class BudApp:
    def __init__(self, iniBud, balance):
        self.iniBud = iniBud
        self.balance = balance
        self.usr_bills = []
        self.bill_due = []
        self.transaction = 0.0
        self.spent = 0.0
        self.BudLimit = 0.0
        self.BudLim_Check = False
        self.CatLim_Check = {'U': False, 'C': False, 'T': False,
                             'M': False, 'S': False, 'F': False, 'X': False}
        self.categories = {'U': 'Household', 'C': 'Credit', 'T': 'Travel',
                           'M': 'Medical',   'S': 'Shopping', 'F': 'Fun', 'X': 'Misc'}
        self.category_limits = {'U': 0.0, 'C': 0.0, 'T': 0.0,
                                'M': 0.0, 'S': 0.0, 'F': 0.0, 'X': 0.0}
        self.category_spent  = {'U': 0.0, 'C': 0.0, 'T': 0.0,
                                'M': 0.0, 'S': 0.0, 'F': 0.0, 'X': 0.0}
        self.tra_spent    = []
        self.tra_desc     = []
        self.tra_date     = []
        self.cat_letter   = []
        self.tra_category = []
        self.tra_overview = []

    def add_transaction_gui(self, amount, description, category_letter, date):
        formats = ["%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d", "%m/%d/%Y"]

        parsed_date = None
        for f in formats:
            try:
                parsed_date = datetime.strptime(date, f)
                break
            except ValueError:
                continue
        if not parsed_date:
            return False

        category_letter = category_letter.upper()
        if category_letter not in self.categories:
            return False

        if amount >= 0:
            if self.BudLim_Check and self.BudLimit > 0:
                if round(self.spent + amount, 2) > round(self.BudLimit, 2):
                    return False
            if (self.CatLim_Check[category_letter] and
                    self.category_limits[category_letter] > 0 and
                    round(self.category_spent[category_letter] + amount, 2) >
                    round(self.category_limits[category_letter], 2)):
                return False

        self.transaction = amount
        self.tra_spent.append(amount)
        self.tra_desc.append(description if description else None)
        self.tra_date.append(parsed_date)
        self.tra_category.append(self.categories[category_letter])
        self.cat_letter.append(category_letter)

        self.category_spent[category_letter] += amount
        self.balance -= amount
        self.spent   += amount

        self.Gen_Tra()
        return True


    def add_bill_gui(self, amount, due_date_str, label=""):
        from datetime import datetime
        formats = ["%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d", "%m/%d/%Y"]
        parsed = None
        for f in formats:
            try:
                parsed = datetime.strptime(due_date_str, f)
                break
            except ValueError:
                continue
        if not parsed:
            return False
        try:
            amt = float(amount)
            if amt <= 0:
                return False
        except (ValueError, TypeError):
            return False
        self.usr_bills.append(amt)
        self.bill_due.append(parsed)
        self.bill_labels = getattr(self, "bill_labels", [])
        self.bill_labels.append(label.strip() if label else "")
        return True

    def remove_bill_gui(self, index):
        if 0 <= index < len(self.usr_bills):
            del self.usr_bills[index]
            del self.bill_due[index]
            if hasattr(self, "bill_labels") and index < len(self.bill_labels):
                del self.bill_labels[index]
            return True
        return False

    def get_bill_status(self, index):
        from datetime import datetime
        now = datetime.now().date()
        due = self.bill_due[index].date()
        diff = (due - now).days
        if diff > 0:
            return diff, f"Due in {diff} day(s)"
        elif diff == 0:
            return diff, "Due TODAY"
        else:
            return diff, f"Overdue by {abs(diff)} day(s)"

    def Set_Bill(self):
        valid_input = False
        formats = ["%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d", "%m/%d/%Y"]
        while not valid_input:
            try:
                print("\nEnter the bill amount: ", end='$')
                usr_bill = float(input())
                if usr_bill <= 0:
                    print("Invalid bill value. Enter a number greater than 0.\n")
                else:
                    valid_input = True
                    self.usr_bills.append(usr_bill)
            except ValueError:
                print("The value you entered is invalid. Please try again.\n")

        valid_date = False
        while not valid_date:
            print("Enter the bill's due date (YYYY-MM-DD or MM/DD/YYYY): ", end='')
            date = input()
            for f in formats:
                try:
                    parsed_date = datetime.strptime(date, f)
                    self.bill_due.append(parsed_date)
                    valid_date = True
                    break
                except ValueError:
                    continue
            if not valid_date:
                print('The date you entered is invalid. Please try again.\n')
        print(f'\nBill of: ${usr_bill:,.2f} and date: {date} has been set.')

    def Bills_Due(self):
        if not self.bill_due:
            print('\nYou have no bills due. Operation canceled.')
            return
        now = datetime.now().date()
        for i, (due, bill) in enumerate(zip(self.bill_due, self.usr_bills), start=1):
            due_date   = due.date()
            difference = due_date - now
            if difference.days > 0:
                print(f'\nBill #{i}: ${bill:,.2f} is due in {difference.days:,} day(s)!')
            elif difference.days == 0:
                print(f'\nBill #{i}: ${bill:,.2f} is due today!')
            else:
                print(f'\nBill #{i}: ${bill:,.2f} is overdue by {abs(difference.days):,} day(s)!')

    def Remove_Bill(self):
        self.Bills_Due()
        if not self.usr_bills:
            print('\nYou have no bills. Operation canceled.')
            return
        print('\nEnter the bill you want to remove: ', end='')
        valid_input = False
        while not valid_input:
            usr_choice = int(input()) - 1
            if usr_choice in range(len(self.bill_due)):
                valid_input = True
                del self.bill_due[usr_choice], self.usr_bills[usr_choice]
                print('Bill has been removed.')
            else:
                print('Error: Input not in range. Try again: ', end='')

    def Init_Bud(self):
        print(f'\nYour initial budget was ${abs(self.iniBud):,.2f}.')

    def Change_Bud(self):
        valid_input = False
        while not valid_input:
            print('\nDo you want to change the budget? Enter (y/n): ', end='')
            usr_choice = input().upper()
            if usr_choice == 'N':
                print('\nBudget unchanged')
                return
            elif usr_choice == 'Y':
                valid_input = True

        change_input = False
        while not change_input:
            try:
                print("\nEnter your new budget: ", end="$")
                new_bud = float(input())
                if new_bud <= 0:
                    print("Invalid budget value. Please try again.\n")
                else:
                    change_input = True
                    self.iniBud  = new_bud
                    self.balance = new_bud
                    print(f'Budget changed to ${self.iniBud:,.2f}')
                    for s in self.tra_spent:
                        self.balance -= s
            except ValueError:
                print("The value you entered is invalid. Please try again.\n")

    def Balance_left(self):
        bal_pct = (self.balance / self.iniBud) * 100 if self.iniBud else 0
        if self.balance >= 0:
            print(f'\nYou have ${abs(self.balance):,.2f} ({bal_pct:.0f}%) left in your budget.')
        else:
            print(f'\nYou are ${abs(self.balance):,.2f} ({bal_pct:.0f}%) overbudget.')

    def Spent(self):
        spt_percent = (self.spent / self.iniBud) * 100 if self.iniBud else 0
        if self.spent < 0:
            print(f'\nYou spent -${abs(self.spent):,.2f} ({spt_percent:.0f}%) in total')
        else:
            print(f'\nYou spent ${self.spent:,.2f} ({spt_percent:.0f}%) in total')

    def Bud_Limit(self):
        if self.BudLim_Check:
            print(f'\nBudget limit already set: ${self.BudLimit:,.2f}')
            return
        valid_input = False
        while not valid_input:
            print('\nDo you want to set a budget limit? Enter (y/n): ', end='')
            usr_choice = input().upper()
            if usr_choice == 'N':
                print('\nBudget limit not set')
                return
            elif usr_choice == 'Y':
                self.BudLim_Check = True
                valid_input = True
        valid_limit = False
        while not valid_limit:
            print('Set the limit for your budget: $', end='')
            try:
                usr_limit = float(input())
                if usr_limit <= 0:
                    print("\nInvalid budget value. Try again")
                else:
                    valid_limit = True
                    self.BudLimit = usr_limit
                    print(f'\nBudget limit of ${self.BudLimit:,.2f} has been set.')
            except ValueError:
                print('\nThe value you entered is invalid. Try again')

    def RemoveBudLim(self):
        self.BudLim_Check = False
        for i in self.CatLim_Check:
            self.CatLim_Check[i] = False
        self.BudLimit = 0.0
        for i in self.category_limits:
            self.category_limits[i] = 0.0
        print('\nBudget & category limits removed')

    def Cat_Limit(self):
        if not self.BudLim_Check:
            print("\nCan't set a spending limit without a budget limit.")
            return
        valid_input = False
        while not valid_input:
            print('\nDo you want to set a spending limit? Enter (y/n): ', end='')
            usr_choice = input().upper()
            if usr_choice == 'N':
                print('\n Spending limit not set')
                return
            elif usr_choice == 'Y':
                valid_input = True
        valid_cat = False
        while not valid_cat:
            print('\n Which category limit do you want to set?')
            print('-'*42)
            print(' Household (U)      Credit (C)    Travel (T)')
            print('   Medical (M)   Shopping (S)       Fun (F)')
            print('Enter a category: ', end='')
            usr_choice = input().upper()
            if usr_choice in self.categories:
                valid_cat = True
                self.CatLim_Check[usr_choice] = True
            else:
                print('\nInvalid category. Please try again')
        valid_percent = False
        while not valid_percent:
            try:
                print(f'Out of ${self.BudLimit:,.2f}, what percentage do you want to spend on {self.categories[usr_choice]}: ', end='')
                usr_pct = int(input())
                if usr_pct <= 0:
                    print('\nInvalid percentage. Please enter a number greater than 0 ')
                else:
                    valid_percent = True
                    percent = self.BudLimit * (usr_pct / 100)
                    self.category_limits[usr_choice] = percent
                    print(f'\n{self.categories[usr_choice]} limit of ${self.category_limits[usr_choice]:,.2f} has been set.')
            except ValueError:
                print('\nThe value you entered is invalid. Please enter a whole number')

    def RemoveCatLim(self):
        print('\nWhich category limit do you want to remove?')
        print('-'*43)
        print(' Household (U)      Credit (C)    Travel (T)')
        print('   Medical (M)   Shopping (S)       Fun (F)')
        print('Enter a category: ', end='')
        valid_input = False
        while not valid_input:
            usr_choice = input().upper()
            if usr_choice in self.categories:
                valid_input = True
                self.category_limits[usr_choice] = 0.0
                self.CatLim_Check[usr_choice] = False
                print(f'\n{self.categories[usr_choice]} limit has been removed.')
            else:
                print('Incorrect Choice.  Enter again:', end=' ')

    def Transaction(self, category):
        formats = ["%Y-%m-%d", "%m-%d-%Y", "%Y/%m/%d", "%m/%d/%Y"]
        category = self.Category()
        valid_input = False
        valid_date  = False
        while not valid_input:
            try:
                print("\nEnter new transaction: ", end='$')
                usr_tra = float(input())
                if usr_tra < 0:
                    valid_input = True
                    self.transaction = usr_tra
                    self.tra_spent.append(self.transaction)
                    self.category_spent[category] += usr_tra
                else:
                    if round(self.spent + usr_tra, 2) > round(self.BudLimit, 2) and self.BudLim_Check:
                        print(f'You cannot exceed your budget limit of ${self.BudLimit:,.2f}')
                        return
                    if self.CatLim_Check[category] and round(self.category_spent[category] + usr_tra, 2) > round(self.category_limits[category], 2):
                        print(f'You cannot exceed your {self.categories[category]} limit of ${self.category_limits[category]:,.2f}')
                        return
                    valid_input = True
                    self.transaction = usr_tra
                    self.tra_spent.append(self.transaction)
                    self.category_spent[category] += usr_tra
            except ValueError:
                print("The value you entered is invalid. Please try again.\n")

        while not valid_date:
            print("Enter the date of transaction (YYYY-MM-DD or MM/DD/YYYY): ", end='')
            date = input()
            for f in formats:
                try:
                    parsed_date = datetime.strptime(date, f)
                    self.tra_date.append(parsed_date)
                    valid_date = True
                    break
                except ValueError:
                    continue
            if not valid_date:
                print('The date you entered is invalid. Please try again.\n')

        print('Do you want to have a description of the transaction (y/n): ', end='')
        valid_input = False
        while not valid_input:
            usr_choice = input().upper()
            if usr_choice == 'Y':
                valid_input = True
                print("Enter description below:\n")
                usr_input = input()
                self.tra_desc.append(usr_input)
            elif usr_choice == 'N':
                valid_input = True
                self.tra_desc.append(None)
            else:
                print('Incorrect Choice.  Enter again (y/n):', end=' ')

        self.balance -= self.transaction
        self.spent   += self.transaction
        self.Gen_Tra()

    def Gen_Tra(self):
        self.tra_overview = []
        for c, s, d, t in zip(self.tra_category, self.tra_spent, self.tra_desc, self.tra_date):
            self.tra_overview.append((c, s, d, t))

    def Past_Tra(self):
        if not self.tra_overview:
            print('\nYou have no past transactions.')
        else:
            for i, (category, spent, description, date) in enumerate(self.tra_overview, 1):
                if spent < 0:
                    print(f'\n({i}.) {category}: -${abs(spent):,.2f}')
                else:
                    print(f'\n({i}.) {category}: ${spent:,.2f}')
                print(f'Description: {description}')
                print(f'Date of Transaction: {date.date()}')

    def Remove_tra(self):
        self.Past_Tra()
        if not self.tra_overview:
            print('You have no past transactions. Operation canceled')
        else:
            print('\nEnter the transaction you want to remove: ', end='')
            valid_input = False
            while not valid_input:
                usr_choice = int(input()) - 1
                if usr_choice in range(len(self.tra_overview)):
                    valid_input = True
                    amount   = self.tra_spent[usr_choice]
                    category = self.cat_letter[usr_choice]
                    if category in self.category_spent:
                        self.category_spent[category] -= amount
                    self.balance += amount
                    self.spent   -= amount
                    del (self.tra_overview[usr_choice], self.tra_spent[usr_choice],
                         self.tra_category[usr_choice], self.tra_desc[usr_choice],
                         self.tra_date[usr_choice])
                else:
                    print('Error: Input not in range. Try again: ', end='')

    def Category(self):
        print('\n              Categories    ')
        print('-'*38)
        print('Household (U)  Credit (C)  Travel (T)')
        print('  Medical (M) Shopping (S)     Fun (F)')
        print('Enter a category: ', end='')
        valid_input = False
        while not valid_input:
            usr_choice = input().upper()
            if usr_choice in self.categories:
                valid_input = True
                self.tra_category.append(self.categories[usr_choice])
                self.cat_letter.append(usr_choice)
                return usr_choice
            else:
                print('Incorrect Choice.  Enter again:', end=' ')

    def Add_New_Budget(self): pass
    def Remove_Budget(self):  pass
    def Switch_Budget(self):  pass
