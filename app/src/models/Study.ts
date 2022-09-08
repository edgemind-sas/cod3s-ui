import Indicator from "./Indicator";

export default interface Study {
  name: string;
  description: string;
  main_block: string;
  indicators: Array<Indicator>;
  selected_indicators: Array<string>;

  simu_params: {
    nb_runs: number;
    seed: number;
    result_filename: string;
    schedule_from: number;
    schedule_to: number;
    schedule_step: number;
    schedule_unit: number;
    schedule_name: number;
  };
}
