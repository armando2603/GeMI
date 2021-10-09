<template>
    <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title style="text-align:center">
          Genomic Metadata Integration Tool
        </q-toolbar-title>
        <q-btn flat dense to='/' label='Home' />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <div>
      <p class="text-h3">Created By</p>
      <p class="text-h5">Giuseppe Serna</p>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script>
import VueRouter from 'vue-router'
const router = new VueRouter()
export default {
  data () {
    return {
      name: router.name
    }
  }
}
</script>
