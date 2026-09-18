<script setup lang="ts">
import { ref } from 'vue'
defineProps<{loading:boolean}>()
const emit=defineEmits<{generate:[genre:string]}>()
const genre=ref('AI laboratory sabotage')
</script>
<template><main class="landing"><div class="case-mark">CU—001 / GENERATIVE CASE FILE</div><h1>CASE:<br><i>UNKNOWN</i></h1><p>진실은 이미 정해졌다. 당신에게 보이지 않을 뿐.</p><section class="setup"><label>사건 유형<select v-model="genre"><option>AI laboratory sabotage</option><option>hotel murder</option><option>museum artwork replacement</option><option>corporate espionage</option><option>missing-person mystery</option></select></label><div><span class="status-dot"></span> PROCEDURAL VISUALS · NORMAL</div><button :disabled="loading" @click="emit('generate',genre)">{{loading?'사건 구성 중…':'NEW CASE'}}</button></section></main></template>
