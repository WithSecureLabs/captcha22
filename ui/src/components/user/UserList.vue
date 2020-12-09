<template>
  <div>    
    <b-row>
      <b-col md="12">
        <div class="table-responsive">
          <table class="table table-striped">
            <thead>
              <tr>
                <th>Firstname</th>
                <th>Surname</th>                
                <th>Details</th>
                <th>Update</th>
                <th>Delete</th>
              </tr>
            </thead>
            <tbody>
              <user-list-row
              v-for="user in users"
              :key="user.username"
              :user="user"
              @details="detailsUser"
              @update="updateUser"
              @delete="deleteUser"/>
            </tbody>
          </table>
        </div>
      </b-col>
    </b-row>
  </div>
</template>
<script>
import UserService from '@/api-services/user.service';
import UserListRow from '@/components/user/UserListRow';

export default {
  name: 'UserList',
  components: {
    UserListRow
  },
  data() {
    return {
      users: []
    };
  },
  created() {
    this.$store.dispatch('getUserAll').then((response) => {
      this.users = response.data;
    });
  },
  methods: {
    detailsUser(username) {
      console.log('details', username);
      this.$router.push({ name: 'UserDetails', params: {id: username}});
    },
    updateUser(username) {
      console.log('update', username);
      this.$router.push({ name: 'UserUpdate', params: {id: username}});
    },
    deleteUser(username) {
      console.log('delete', username);
      this.$store.dispatch('deleteUser', {username: username}).then(() => {
        this.$store.dispatch('getUserAll').then((response) => {
          this.users = response.data;
        });
      }).catch(() => {
        alert("Failed to delete user. Unknown error.")
      });
    }
  }
};
</script>