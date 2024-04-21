from supermemo2 import SMTwo

result = SMTwo.first_review(0)
print(result)

while True:
    result = SMTwo(result.easiness, result.interval, result.repetitions).review(int(input('Option: ')))
    print(result)