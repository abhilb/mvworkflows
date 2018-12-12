from local.operator import Operator
from local import Operators

def test_operator():
    for op_type in Operators.keys():
        print("---------------------")
        op_name = "test"
        print(f"Type: {op_type} Name: {op_name}")
        op = Operator(op_type, op_name)
        print(op.to_json())
    print("---------------------")

if __name__  == "__main__":
    test_operator()
