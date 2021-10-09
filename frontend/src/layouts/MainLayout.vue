
<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title style="text-align:center">
          Genomic Metadata Integration Tool
        </q-toolbar-title>
        <q-btn flat dense to='/about' label='about' />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>
