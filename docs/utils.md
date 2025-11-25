#define DECLARE_DIRECTIVE(NAME) #region "%{NAME:esc}"
#define DECLARE_END_DIRECTIVE #endregion\
---\

#define TODO(MSG) ***TODO:** %MSG*\
#warning "TODO: %{MSG:esc}"
