<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import type { Game } from '../types'
const props=defineProps<{game:Game;loading:boolean;streamed:string}>()
const emit=defineEmits<{act:[text:string];accuse:[suspect:string,reasoning:string];newCase:[]}>()
const input=ref(''); const tab=ref<'evidence'|'suspects'>('evidence'); const showBriefing=ref(!props.game.completed); const showCaseFile=ref(false); const showAccuse=ref(false); const selected=ref(''); const reasoning=ref('')
const location=computed(()=>props.game.locations.find(x=>x.id===props.game.current_location_id)!)
const briefingStep=ref(0); const briefingText=ref('')
const briefingLines=computed(()=>[props.game.title,props.game.introduction,props.game.incident_summary])
const briefingImage=computed(()=>briefingStep.value===1?'/briefing/location-lobby.jpg':'/briefing/cover.jpg')
let typingTimer:ReturnType<typeof globalThis.setInterval>|undefined; let advanceTimer:ReturnType<typeof globalThis.setTimeout>|undefined
function clearBriefingTimers(){globalThis.clearInterval(typingTimer);globalThis.clearTimeout(advanceTimer)}
function playBriefingStep(){clearBriefingTimers();if(briefingStep.value>2)return;const line=briefingLines.value[briefingStep.value];let i=0;briefingText.value='';typingTimer=globalThis.setInterval(()=>{briefingText.value=line.slice(0,++i);if(i===line.length){globalThis.clearInterval(typingTimer);advanceTimer=globalThis.setTimeout(()=>{briefingStep.value++;playBriefingStep()},2600)}},briefingStep.value===0?140:75)}
function openBriefing(){showBriefing.value=true;briefingStep.value=0;playBriefingStep()}
function skipBriefing(){clearBriefingTimers();briefingStep.value=3}
function closeBriefing(){clearBriefingTimers();showBriefing.value=false}
onMounted(()=>{if(showBriefing.value)playBriefingStep()});onBeforeUnmount(clearBriefingTimers)
function send(text=input.value){ if(!text.trim())return; emit('act',text); input.value='' }
function confirm(){if(selected.value&&reasoning.value.trim()){emit('accuse',selected.value,reasoning.value);showAccuse.value=false}}
</script>
<template><div class="game-shell">
  <header><b>CASE: <i>UNKNOWN</i></b><span class="file-no">{{game.id.slice(0,8)}} · ACTIVE FILE</span><button class="ghost case-toggle" @click="showCaseFile=!showCaseFile">사건 정보</button><button class="ghost briefing-replay" @click="openBriefing">브리핑 다시보기</button><button class="ghost" @click="emit('newCase')">새 사건</button></header>
  <aside class="case-file" :class="{open:showCaseFile}"><small>CASE FILE / {{game.genre}}</small><h2>{{game.title}}</h2><p>{{game.incident_summary}}</p><div class="progress"><span :style="{width:`${Math.min(100,game.evidence.length/7*100)}%`}"></span></div><small>{{game.evidence.length}} EVIDENCE RECOVERED</small><h3>LOCATIONS</h3><button v-for="loc in game.locations" :key="loc.id" class="nav-item" :class="{active:loc.id===game.current_location_id}" :disabled="loc.locked" @click="send(`${loc.name}로 이동`)" :aria-label="loc.name"><span>{{loc.locked?'▣':'◇'}}</span>{{loc.name}}</button>
  <h3>QUICK ACTIONS</h3><button class="quick" @click="send('주변을 자세히 조사해')">⌕ 주변 조사</button><button class="quick" @click="send('현재 증거 정리해줘')">≡ 증거 정리</button></aside>
  <main class="investigation"><div class="scene"><img :src="location.image_url" :alt="location.name"><div><small>CURRENT LOCATION</small><h2>{{location.name}}</h2><p>{{location.description}}</p></div></div><section class="log" aria-live="polite"><article v-for="(line,i) in game.narratives" :key="i" :class="i===game.narratives.length-1?'latest':''"><small>{{i===0?'CASE BRIEF':'FIELD NOTE'}}</small><p>{{i===game.narratives.length-1&&streamed?streamed:line}}</p></article></section><form @submit.prevent="send()"><label for="action">무엇을 조사하시겠습니까?</label><div class="input-row"><input id="action" v-model="input" :disabled="loading||game.completed" placeholder="예: CCTV와 출입 기록을 확인해"><button :disabled="loading||!input.trim()">전송</button></div></form></main>
  <aside class="board"><nav><button :class="{active:tab==='evidence'}" @click="tab='evidence'">EVIDENCE {{game.evidence.length}}</button><button :class="{active:tab==='suspects'}" @click="tab='suspects'">SUSPECTS</button></nav><div v-if="tab==='evidence'" class="card-grid"><article v-for="item in game.evidence" :key="item.id" class="evidence-card"><img v-if="item.image_url" :src="item.image_url" :alt="item.title"><small>{{item.category}}</small><h4>{{item.title}}</h4><p>{{item.description}}</p></article><div v-if="!game.evidence.length" class="empty">아직 확보한 증거가 없습니다.<br>현장을 조사하세요.</div></div><div v-else class="suspects"><article v-for="s in game.suspects" :key="s.id"><img :src="s.portrait_url" :alt="s.name"><div><h4>{{s.name}}</h4><small>{{s.role}}</small><p>{{s.public_profile}}</p><button class="quick" @click="send(`${s.name}에게 알리바이를 물어봐`)">심문</button></div></article></div><button class="accuse" :disabled="game.completed" @click="showAccuse=true">용의자 고발</button></aside>
  <nav class="mobile-nav"><button>수사</button><button @click="tab='evidence'">증거</button><button @click="tab='suspects'">용의자</button></nav>
  <div v-if="showBriefing" class="briefing" role="dialog" aria-modal="true" aria-labelledby="briefing-title">
    <div v-if="briefingStep===2" class="briefing-portraits"><img v-for="suspect in game.suspects" :key="suspect.id" :src="`/briefing/suspect-${suspect.id}.jpg`" :alt="suspect.name"></div>
    <img v-else class="briefing-backdrop" :src="briefingImage" :alt="briefingStep===1?game.locations[0]?.name:`${game.title} 사건 현장`"><div class="briefing-shade"></div>
    <div class="briefing-top"><span>CASE {{game.id.slice(0,8).toUpperCase()}}</span><button class="briefing-skip" @click="skipBriefing">건너뛰기</button></div>
    <section v-if="briefingStep<3" class="briefing-story">
      <small>0{{briefingStep+1}} / 03 · INCIDENT BRIEFING</small>
      <h1 v-if="briefingStep===0" id="briefing-title">{{briefingText}}<i></i></h1><p v-else>{{briefingText}}<i></i></p>
      <div class="briefing-progress"><span v-for="n in 3" :key="n" :class="{active:n<=briefingStep+1}"></span></div>
    </section>
    <section v-else class="briefing-summary">
      <small>FIELD GUIDE / 수사 지침</small><h2 id="briefing-title">진실은 행동 속에 남아 있습니다.</h2>
      <ol class="briefing-guide"><li><b>01</b><span><strong>현장 이동</strong>조사할 장소를 선택하세요.</span></li><li><b>02</b><span><strong>단서 조사</strong>CCTV와 로그 등 대상을 구체적으로 조사하세요.</span></li><li><b>03</b><span><strong>심문과 정리</strong>진술과 증거를 비교하세요.</span></li><li><b>04</b><span><strong>최종 고발</strong>범인과 근거를 선택하세요.</span></li></ol>
      <button class="briefing-start" @click="closeBriefing">수사 시작 <span>→</span></button>
    </section>
  </div>
  <div v-if="showAccuse" class="modal" @click.self="showAccuse=false"><section><small>FINAL ACCUSATION</small><h2>한 번의 고발로 사건이 끝납니다.</h2><label>용의자<select v-model="selected"><option value="" disabled>선택</option><option v-for="s in game.suspects" :value="s.id" :key="s.id">{{s.name}}</option></select></label><label>추론<textarea v-model="reasoning" placeholder="증거를 연결해 설명하세요"></textarea></label><div><button class="ghost" @click="showAccuse=false">취소</button><button class="accuse" :disabled="!selected||reasoning.length<3" @click="confirm">고발 확정</button></div></section></div>
  <div v-if="game.completed" class="modal resolution"><section><small>{{game.won?'CASE SOLVED':'CASE FAILED'}}</small><h2>{{game.won?'진실을 밝혀냈습니다.':'진실은 다른 곳에 있었습니다.'}}</h2><p>{{game.solution?.summary}}</p><dl><dt>범행 시각</dt><dd>{{game.solution?.crime_time}}</dd><dt>동기</dt><dd>{{game.solution?.motive}}</dd><dt>수법</dt><dd>{{game.solution?.crime_method}}</dd></dl><ol><li v-for="step in game.solution?.timeline" :key="step">{{step}}</li></ol><button @click="emit('newCase')">NEW CASE</button></section></div>
</div></template>
