<script setup lang="ts">
import { onMounted, ref } from 'vue'
import CaseSetup from './components/CaseSetup.vue'
import Investigation from './components/Investigation.vue'
import { useGameStore } from './stores/game'
const store=useGameStore(); const landing=ref(true)
async function create(genre:string){await store.create(genre);if(store.game)landing.value=false}
onMounted(async()=>{try{const c=await fetch('/api/config/public').then(r=>r.json());if(c.latest_case_id){await store.load(c.latest_case_id);landing.value=false}}catch{/* backend status is shown below */}})
</script>
<template><CaseSetup v-if="landing||!store.game" :loading="store.loading" @generate="create"/><Investigation v-else :game="store.game" :loading="store.loading" :streamed="store.streamed" @act="store.act" @accuse="store.accuse" @new-case="landing=true"/><div v-if="store.error" class="toast">{{store.error}}</div></template>
