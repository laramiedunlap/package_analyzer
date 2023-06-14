import pandas as pd
import numpy as np
import numpy_financial as npf
from collections import OrderedDict


# I need to add in kwargs for price, yield, settlement date.
def amortize(interest_rate: float, begLoanBalance: float, begMonths: int)-> OrderedDict:
    """Create an OrderedDict with a loan's expected amortization schedule"""
    """NOTE: This will work for most loans, however there are loans that have quarterly payments. So there 
    should be another method that checks periodicity of loan payments."""
    count = 0 
    beg_period_balance = begLoanBalance
    remaining_months = begMonths    
    schedLoanPmt = round(npf.pmt((interest_rate/12), begMonths, begLoanBalance*-1), 0)
    
    while schedLoanPmt > 0:
        try: 
            # Calculate payment
            schedLoanPmt = round(npf.pmt((interest_rate/12), remaining_months, beg_period_balance*-1), 0)
            # Calculate scheduled interest
            schedInterestPmt = round(beg_period_balance*(interest_rate/12), 0)
            # Check to see if this payment will pay off the loan
            pmt = min(schedLoanPmt, beg_period_balance + schedInterestPmt)
            # Calculate scheduled principal
            schedPrincipal = round(pmt - schedInterestPmt, 2)
            # Calculate Unscheduled Principal
            # NOTE -- Add in CPR here
            # Calculate Ending Loan Balance
            # NOTE -- If you add-in CPR, then you'll need to add the unscheduled principal to scheduled principal
            endingLoanBalance = round(beg_period_balance - schedPrincipal,0)
            count += 1
            yield OrderedDict([('Month', count), 
                            ('Begging Loan Balance', beg_period_balance),
                            ('Scheduled Loan Payment', pmt),
                            ('Scheduled Interest Payment', schedInterestPmt),
                            ('Scheduled Principal', schedPrincipal),
                            ('Ending Loan Balance', endingLoanBalance)])
            beg_period_balance = endingLoanBalance
            remaining_months -= 1
            
        except IndexError:
            print(f"error at index: {count}")
            
