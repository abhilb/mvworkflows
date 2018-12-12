from local.workflow import Workflow


def test_workflow():
    w = Workflow("w")
    w.add_operator("file_capture")
    w.add_operator("file_capture")
    w.add_operator("file_capture")
    print(w.save())

if __name__ == "__main__":
    test_workflow()
