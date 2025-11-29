{{/*
Expand the name of the chart.
*/}}
{{- define "kratos-auth.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "kratos-auth.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "kratos-auth.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "kratos-auth.labels" -}}
helm.sh/chart: {{ include "kratos-auth.chart" . }}
{{ include "kratos-auth.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "kratos-auth.selectorLabels" -}}
app.kubernetes.io/name: {{ include "kratos-auth.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Database DSN
*/}}
{{- define "kratos-auth.dsn" -}}
{{- if eq .Values.kratos.database.type "postgres" }}
postgres://{{ .Values.kratos.database.user }}:{{ .Values.kratos.database.password }}@{{ .Values.kratos.database.host }}:{{ .Values.kratos.database.port }}/{{ .Values.kratos.database.database }}?sslmode=disable&max_conns=20&max_idle_conns=4
{{- else }}
memory
{{- end }}
{{- end }}
