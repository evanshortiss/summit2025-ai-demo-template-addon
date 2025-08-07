{{/*
Expand the name of the chart.
*/}}
{{- define "langchain-agent-build.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "langchain-agent-build.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "langchain-agent-build.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "langchain-agent-build.labels" -}}
backstage.io/kubernetes-id: {{ .Values.app.name }}
helm.sh/chart: {{ include "langchain-agent-build.chart" . }}
{{ include "langchain-agent-build.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "langchain-agent-build.selectorLabels" -}}
app.kubernetes.io/name: {{ include "langchain-agent-build.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the image reference for dev environment
*/}}
{{- define "image.dev-url" -}}
{{- printf "%s/%s/%s" .Values.image.registry .Values.image.organization .Values.image.name -}}
{{- end }}