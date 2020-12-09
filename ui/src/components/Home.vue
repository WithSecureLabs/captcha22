<template>
  <p class="homeText">
    WELCOME TO
    <img class="logo" src="../assets/CAPTCHA22.svg" />
  </p>
</template>
<script>
import UserService from '@/api-services/user.service';
export default {
  name: 'Home'  
};
</script>
<style scoped>
.homeText{
    font-size: 35px;
    color: black;
    text-align: center;
    position: relative;
    top:30px;
    text-shadow: 2px 2px 2px gray;
}
</style>