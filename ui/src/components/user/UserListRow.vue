<template>
  <tr>
    <td>{{ user.firstname }}</td>
                <td>{{ user.surname }}</td>                
                <td>
                  <b-button variant="outline-primary"
                  @click="onDetailsClick">Details</b-button>
                </td>
                <td>
                  <b-button variant="success"
                  @click="onUpdateClick">Update</b-button>
                </td>
                <td>
                  <b-button variant="danger"
                  @click="onDeleteClick">Delete</b-button>
                </td>
  </tr>
</template>
<script>
export default {
  name: 'UserListRow',
  props: [ 'user' ],
  methods: {
      onDetailsClick() {
          this.$emit('details', this.user.username);
      },
      onUpdateClick() {
          this.$emit('update', this.user.username);
      },
      onDeleteClick() {
          this.$emit('delete', this.user.username);
      }
  }
};
</script>