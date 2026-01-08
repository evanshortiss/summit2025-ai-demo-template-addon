{{/*
Expand the name of the chart.
*/}}
{{- define "langchain-agent.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "langchain-agent.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "langchain-agent.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "backstage.labels" -}}
backstage.io/kubernetes-id: {{ .Values.app.name }}
{{- end }}

{{- define "langchain-agent.labels" -}}
backstage.io/kubernetes-id: {{ .Values.app.name }}
helm.sh/chart: {{ include "langchain-agent.chart" . }}
app.openshift.io/runtime: python
{{ include "langchain-agent.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "langchain-agent.selectorLabels" -}}
app.kubernetes.io/name: {{ include "langchain-agent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "langchain-agent.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "langchain-agent.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the image reference
*/}}
{{- define "langchain-agent.image" -}}
{{- $tag := .Values.image.tag | default "latest" -}}
{{- if eq .Values.image.registry "Quay" }}
{{- printf "%s/%s/%s:%s" .Values.image.host .Values.image.organization .Values.image.name $tag -}}
{{- else }}
{{- printf "%s/%s/%s:%s" .Values.image.host .Values.image.organization .Values.image.name $tag -}}
{{- end }}
{{- end }}