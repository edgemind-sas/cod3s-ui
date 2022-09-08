import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';
import VueMoment from 'vue-moment';

import colors from 'vuetify/lib/util/colors'

Vue.use(Vuetify);
Vue.use(VueMoment);

export default new Vuetify({
  // #1e3d59, #f5f0e1, #ff6e40, #ffc13b
    theme: {
        themes: {
          light: {
            primary: '#26495c',
            secondary: '#c4a35a',
            accent:"#c66b3d",
          },
        },
      },
});
