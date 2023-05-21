package handlers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"

	"github.com/CCTVBackend/pkg/models"
	"github.com/gorilla/mux"
)

func (h handler) CreateAccess(w http.ResponseWriter, r *http.Request) {

	//Read request body
	defer r.Body.Close()
	body, err := io.ReadAll(r.Body)

	if err != nil {
		log.Fatalln(err)
	}

	var access models.Access
	json.Unmarshal(body, &access)

	//add to database and check if error
	if result := h.DB.Create(&access); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusCreated)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Created")
}

func (h handler) ReadAccess(w http.ResponseWriter, r *http.Request) {

	//Get id from URL
	vars := mux.Vars(r)
	c_id, _ := strconv.Atoi(vars["cid"])
	p_id, _ := strconv.Atoi(vars["pid"])

	// find access in db
	var access models.Access
	if result := h.DB.First(&access, "camera_id = ? AND person_id = ?", c_id, p_id); result.Error != nil {
		//log error and return status BadRequest
		// log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		w.Write([]byte("Failed"))
		return
	}

	//Return status Created
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode(access)
}

func (h handler) UpdateAccess(w http.ResponseWriter, r *http.Request) {
	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	//Read request body
	body, err := io.ReadAll(r.Body)
	if err != nil {
		log.Fatalln(err)
	}

	var access models.Access
	//Find access in DB
	result := h.DB.First(&access, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Overwrite access data
	var newAccess models.Access
	json.Unmarshal(body, &newAccess)
	access = newAccess

	//Push changes to DB
	h.DB.Save(&access)

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Updated")

}
func (h handler) DeleteAccess(w http.ResponseWriter, r *http.Request) {

	//Get Id from URL,
	vars := mux.Vars(r)
	id, _ := strconv.Atoi(vars["id"])

	var access models.Access

	//Find access in DB
	result := h.DB.First(&access, id)
	if result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//Delete access in DB
	if result := h.DB.Delete(&access); result.Error != nil {
		//log error and return status BadRequest
		log.Println(result.Error)
		w.WriteHeader(http.StatusBadRequest)
		w.Header().Add("Content-Type", "application/json")
		json.NewEncoder(w).Encode("Failed")
		return
	}

	//return ok
	w.WriteHeader(http.StatusOK)
	w.Header().Add("Content-Type", "application/json")
	json.NewEncoder(w).Encode("Deleted")

}
