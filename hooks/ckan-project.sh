# Shared by the hooks. is_ckan_extension succeeds when the session's project is
# a CKAN extension, or a folder holding extensions under src/, but not when it
# is a CKAN core checkout. It reads only directory names.

is_ckan_extension() {
    dir=${CLAUDE_PROJECT_DIR:-$PWD}
    [ -f "$dir/ckan/__init__.py" ] && return 1  # a CKAN core checkout
    case ${dir##*/} in ckanext-*) return 0 ;; esac
    [ -d "$dir/ckanext" ] && return 0
    for path in "$dir"/src/ckanext-*; do
        [ -d "$path" ] && return 0
    done
    return 1
}
