import StudyType from "@/models/StudyType";
import Workspace from "@/models/Workspace";

class FakeService {
  getFakeWorkspaces(): Array<Workspace> {
    const workspaces: Array<Workspace> = [];

    const workspace1 = new Workspace();
    workspace1.name = "Pycatshoo WS";
    workspace1.type = StudyType.PYCATSHOO;
    workspace1.path = "/home/gurvan/tmp/code3s-ws/pycatshoo";

    workspaces.push(workspace1);

    const workspace2 = new Workspace();
    workspace2.name = "Altarica WS";
    workspace2.type = StudyType.AR3;
    workspace2.path = "/home/gurvan/dev/cod3s/cod3s-ui/examples/train";
    workspaces.push(workspace2);

    const workspace3 = new Workspace();
    workspace3.name = "Another WS";
    workspace3.type = StudyType.AR3;
    workspace3.path = "/home/gurvan/dev/cod3s/cod3s-ui/examples/train";
    workspaces.push(workspace3);

    const workspace4 = new Workspace();
    workspace4.name = "Another WS";
    workspace4.type = StudyType.PYCATSHOO;
    workspace4.path = "/home/gurvan/dev/cod3s/cod3s-ui/examples/train";
    workspaces.push(workspace4);

    return workspaces;
  }
}

export default new FakeService();
