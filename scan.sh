echo "task copyDependencies(type: Copy) {from configurations.compile into 'dependencies'}" >> $CI_PROJECT_DIR/$CI_PROJECT_NAME-web/$CI_PROJECT_NAME-web.gradle
$CI_PROJECT_DIR/gradlew $CI_PROJECT_NAME-web:copyDependencies
zip -r $CI_PROJECT_NAME-web/dependencies.zip $CI_PROJECT_NAME-web/dependencies
pip install -r $CI_PROJECT_DIR/cx/requirements.txt
python $CI_PROJECT_DIR/cx/scan.py --repo_name=$CI_PROJECT_NAME --username=$CxUSER --password=$CxPASS --osa
