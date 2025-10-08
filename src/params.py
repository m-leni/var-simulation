"""Risk tolerance quiz parameters and scoring."""

RISK_TOLERANCE_QUESTIONS = [
    ("In general, how would your best friend describe you as a risk taker?",
     ["A. A real gambler",
      "B. Willing to take risks after completing adequate research",
      "C. Cautious",
      "D. A real risk avoider"],
     {"A":4, "B":3, "C":2, "D":1}),

    ("You are on a TV game show and can choose one of the following. Which would you take?",
     ["A. $1,000 in cash",
      "B. A 50% chance at winning $5,000",
      "C. A 25% chance at winning $10,000",
      "D. A 5% chance at winning $100,000"],
     {"A":1, "B":2, "C":3, "D":4}),

    ("You have just finished saving for a once-in-a-lifetime vacation. Three weeks before you plan to leave, you lose your job. You would:",
     ["A. Cancel the vacation",
      "B. Take a much more modest vacation",
      "C. Go as scheduled, reasoning that you need the time to prepare for a job search",
      "D. Extend your vacation because this might be your last chance to go first-class"],
     {"A":1, "B":2, "C":3, "D":4}),

    ("If you unexpectedly received $20,000 to invest, what would you do?",
     ["A. Deposit it in a bank account, money market fund, or insured CD",
      "B. Invest it in safe high-quality bonds or bond mutual funds",
      "C. Invest it in stocks or stock mutual funds"],
     {"A":1, "B":2, "C":3}),

    ("In terms of experience, how comfortable are you investing in stocks or stock mutual funds?",
     ["A. Not at all comfortable",
      "B. Somewhat comfortable",
      "C. Very comfortable"],
     {"A":1, "B":2, "C":3}),

    ("When you think of the word 'risk,' which of the following words comes to mind first?",
     ["A. Loss",
      "B. Uncertainty",
      "C. Opportunity",
      "D. Thrill"],
     {"A":1, "B":2, "C":3, "D":4}),

    ("Some experts are predicting prices of assets such as gold, jewels, collectibles, and real estate to increase, while the stock market is expected to decline. If you owned stock investments, what would you do?",
     ["A. Hold what you have",
      "B. Sell your stocks and invest in assets expected to increase in value",
      "C. Sell your stocks and put the money in a bank account or money market fund"],
     {"A":3, "B":2, "C":1}),

    ("Given the best and worst case returns of the four investment choices below, which would you prefer?",
     ["A. $200 gain / $0 loss",
      "B. $800 gain / $200 loss",
      "C. $2,600 gain / $800 loss",
      "D. $4,800 gain / $2,400 loss"],
     {"A":1, "B":2, "C":3, "D":4}),

    ("In addition to whatever you own, you have been given $1,000. You are now asked to choose between:",
     ["A. A sure gain of $500",
      "B. A 50% chance to gain $1,000 and a 50% chance to gain nothing"],
     {"A":1, "B":2}),

    ("In addition to whatever you own, you have been given $2,000. You are now asked to choose between:",
     ["A. A sure loss of $500",
      "B. A 50% chance to lose $1,000 and a 50% chance to lose nothing"],
     {"A":1, "B":2}),

    ("Suppose a relative left you an inheritance of $100,000, stipulating that you must invest all of it in one of the following choices. Which would you select?",
     ["A. A savings account or money market mutual fund",
      "B. A mutual fund that owns stocks and bonds",
      "C. A portfolio of 15 common stocks",
      "D. Commodities like gold, silver, and oil"],
     {"A":1, "B":2, "C":3, "D":4}),

    ("If you had to invest $20,000, which investment would you select?",
     ["A. 60% low-risk / 30% medium-risk / 10% high-risk",
      "B. 30% low-risk / 40% medium-risk / 30% high-risk",
      "C. 10% low-risk / 40% medium-risk / 50% high-risk"],
     {"A":1, "B":2, "C":3}),

    ("Your trusted friend and financial advisor suggests a 'once in a lifetime' investment. If you invest, you could double your money, but you could also lose half. What would you do?",
     ["A. Invest nothing",
      "B. Invest a small portion",
      "C. Invest about half of what you could afford",
      "D. Invest all you could afford"],
     {"A":1, "B":2, "C":3, "D":4})
]