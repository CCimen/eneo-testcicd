<!--
    Copyright (c) 2024 Sundsvalls Kommun

    Licensed under the MIT License.
-->

<script lang="ts">
  import { IconAssistants } from "@intric/icons/assistants";
  import { IconSession } from "@intric/icons/session";
  import { IconQuestionMark } from "@intric/icons/question-mark";
  import { IconLoadingSpinner } from "@intric/icons/loading-spinner";
  import { Page, Settings } from "$lib/components/layout";

  import InteractiveGraph from "./InteractiveGraph.svelte";
  import TenantAssistantTable from "./TenantAssistantTable.svelte";
  import { writable } from "svelte/store";

  export let data;

  let selectedTab = writable<string>();
</script>

<svelte:head>
  <title>Eneo.ai – Admin – Insights</title>
</svelte:head>

<Page.Root tabController={selectedTab}>
  <Page.Header>
    <Page.Title title="Insights"></Page.Title>
    <Page.Tabbar>
      <Page.TabTrigger tab="overview">Usage</Page.TabTrigger>
      <Page.TabTrigger tab="assistants">Assistants</Page.TabTrigger>
    </Page.Tabbar>
  </Page.Header>
  <Page.Main>
    <Page.Tab id="overview">
      {#if $selectedTab === "overview"}
        <Settings.Page>
          <Settings.Group title="Statistics">
            <Settings.Row
              fullWidth
              title="Assistant usage"
              description="Discover how people are interacting with your organsisation's assistants."
            >
              <div class="h-[600px]">
                <div
                  class="relativ border-stronger flex h-full w-full items-stretch overflow-clip rounded-lg border shadow"
                >
                  {#await data.data}
                    <div class="flex h-full w-full items-center justify-center">
                      <div class="flex flex-col items-center justify-center gap-2 pt-3">
                        <IconLoadingSpinner class="animate-spin" />
                        Loading data...
                      </div>
                    </div>
                  {:then loadedData}
                    <InteractiveGraph data={loadedData} timeframe={data.timeframe}
                    ></InteractiveGraph>

                    <div class="border-stronger bg-hover-dimmer flex flex-grow flex-col border-l">
                      <div class="border-stronger flex h-1/3 flex-col justify-between border-b p-6">
                        <div class="flex gap-2">
                          <IconAssistants />
                          Assistants created
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.assistants.length}</span
                        >
                      </div>

                      <div class="border-stronger flex h-1/3 flex-col justify-between border-b p-6">
                        <div class="flex gap-2">
                          <IconSession />
                          Conversations started
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.sessions.length}</span
                        >
                      </div>

                      <div class="border-stronger flex h-1/3 flex-col justify-between p-6">
                        <div class="flex gap-2">
                          <IconQuestionMark />
                          Questions asked
                        </div>
                        <span class="self-end text-[2.75rem] font-medium"
                          >{loadedData.questions.length}</span
                        >
                      </div>
                    </div>
                  {/await}
                </div>
              </div>
            </Settings.Row>
          </Settings.Group>
        </Settings.Page>
      {/if}
    </Page.Tab>
    <Page.Tab id="assistants">
      <TenantAssistantTable assistants={data.assistants} />
    </Page.Tab>
  </Page.Main>
</Page.Root>
