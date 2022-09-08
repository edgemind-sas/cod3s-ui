import StudyType from "@/models/StudyType";

class AppService {
  getStudyType(): StudyType {
    const sudyType = localStorage.getItem("studyType");
    if (sudyType != null) {
      return sudyType as StudyType;
    } else {
      return StudyType.AR3;
    }
  }
}

export default new AppService();
