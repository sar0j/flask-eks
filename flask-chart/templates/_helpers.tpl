{{/*
Common labels
*/}}
{{- define "flask-chart.labels" -}}
app: {{ .Values.app.name }}
version: {{ .Values.app.version }}
chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "flask-chart.selectorLabels" -}}
app: {{ .Values.app.name }}
{{- end }}
