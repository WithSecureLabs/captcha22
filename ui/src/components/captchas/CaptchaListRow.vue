<template>
  <tr>                
                <td> {{ captcha.modelNumber }}</td>

                <td v-if="captcha.busyTraining">
                  <b-icon icon="circle-fill" animation="fade" font-scale="1" variant="warning"></b-icon>
                </td>
                <td v-else>  
                  <b-icon icon="check-circle-fill" font-scale="1" variant="success"></b-icon>
                </td>
                
                <td v-if="captcha.hasModel">
                  <b-icon icon="check-circle-fill" font-scale="1" variant="success"></b-icon>                  
                </td>
                <td v-else>
                  <b-icon icon="x-circle-fill" font-scale="1" variant="danger"></b-icon>                  
                </td>
                <td v-if="captcha.modelActive">
                  <b-icon icon="check-circle-fill" animation="fade" font-scale="1" variant="success"></b-icon>
                </td> 
                <td v-else>
                  <b-icon icon="x-circle-fill" font-scale="1" variant="danger"></b-icon>                  
                </td>
                <td>
                  <b-button variant="outline-primary"
                  @click="onDetailsClick">Details</b-button>
                </td>                             
  </tr>
</template>
<script>
export default {
  name: 'CaptchaListRow',
  props: [ 'captcha' ],
  methods: {
      onDetailsClick() {
          this.$emit('details', this.captcha.uri.split("/")[this.captcha.uri.split("/").length - 1]);
      },
  },
  computed: {
    isAuthenticated () {      
      return this.$store.getters.isAuthenticated;
    },
    isEmployee () {
      return this.$store.getters.isEmployee;
    },
    isCustomer () {
      return this.$store.getters.isCustomer;
    }
  }
};
</script>