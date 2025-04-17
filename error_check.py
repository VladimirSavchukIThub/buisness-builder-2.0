try:
    import os
    print("1. Imported os")
    
    import datetime
    print("2. Imported datetime")
    
    from bank_api import BankAPI, get_business_loan_rates, calculate_business_loan
    print("3. Imported bank_api modules")
    
    from pdf_generator import PDFGenerator
    print("4. Imported PDF Generator")
    
except Exception as e:
    import traceback
    print("Error occurred:")
    print(traceback.format_exc()) 