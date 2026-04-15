<script setup lang="ts">

import Section from "../Section.vue";
import ITNCard from "./ITNCard.vue";



</script>
<template>
    <div>
        <Section :title="'LES INFORMATIONS À RETENIR'">
          <div class="flex gap-5">
               <ITNCard />
                <ITNCard />
            <ITNCard />
          </div>
          
        </Section>
    </div>
</template>

