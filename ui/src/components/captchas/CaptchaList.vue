<template>
  <div>      
    <b-row>
      <b-col md="12">
        <div class="table-responsive">  
          <div class="accordion" role="tablist">      
            <b-card no-body class="md-1" v-for="title in this.titles" :key="title">
              <b-card-header header-tag="header" class="p-1" role="tab">
                <b-button block v-b-toggle="'accordion' + title" variant="dark">{{ title }}</b-button>
              </b-card-header>
              <b-collapse :id="'accordion' + title" accordion="my-accordion" role="tabpanel">
                <b-card-body>                  
                  <table class="table table-striped">
                    <thead>
                      <tr>                        
                        <th>Model Number</th>                
                        <th>Model Trained</th>
                        <th>Model Stored</th>
                        <th>Model Active</th>
                        <th>Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      <captcha-list-row
                      v-for="captcha in orderedCaptchas(title)"
                      :key="captcha.uri"
                      :captcha="captcha"
                      @details="detailsCaptcha"              
                      />
                    </tbody>
                  </table>
                </b-card-body>
              </b-collapse>
            </b-card>
          </div>
        </div>
      </b-col>
    </b-row>
  </div>
</template>
<script>

import CaptchaService from '@/api-services/captchas.service';
import CaptchaListRow from '@/components/captchas/CaptchaListRow';

export default {
  name: 'CaptchaList',
  components: {
    CaptchaListRow   
  },

  computed: {
    isAuthenticated () {      
      return this.$store.getters.isAuthenticated;
    },       
  },
  data() {
    return {
      captchas: [],
      titles: [],
      isOpen: [],      
    };
  },
  created() {
    this.$store.dispatch('getCaptchaAll').then((response) => {
      this.captchas = response.data.captchas;

      for (var i = 0; i < this.captchas.length; i++)
      {
        this.titles.push(this.captchas[i].title);
      }

      function onlyUnique(value, index, self)
      {
        return self.indexOf(value) === index;
      }

      this.titles = this.titles.filter(onlyUnique).sort();

      console.log(this.titles);


    });
  },
  methods: {    
    
    detailsCaptcha(uri) {
      console.log('details', uri);
      this.$router.push({ name: 'CaptchaDetails', params: {id: uri}});
    },
    orderedCaptchas: function(title) {
      var captchaList = [];
      for (var i = 0; i < this.captchas.length; i++)
      {
        if(this.captchas[i].title == title)
        {
          captchaList.push(this.captchas[i]);
        }
      }

      return _.orderBy(captchaList, ['modelNumber'], ['asc']);
    },
  }
};
</script>