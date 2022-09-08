import Observer from "./Observer";

export default interface Block {
  name: string;
  filename: string;
  observers: Array<Observer>;
}
